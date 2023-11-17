import decimal
from decimal import Decimal
from copy import deepcopy

from django.apps import apps
from django.conf import settings
from django.db import transaction

from .models import Assembly, AssemblyComponent
from product.models import Product


class UserAssembly:
    def __init__(self, request):
        """
        Initialize the current user Assembly.
        """
        self.session = request.session
        data = self.session.get(settings.ASSEMBLY_SESSION_ID)

        if not data:
            # save an empty user_assembly in the session
            name, user_assembly, status = self.session[settings.ASSEMBLY_SESSION_ID] = [self.default_assembly_name(),
                                                                                        {},
                                                                                        request.user.is_authenticated]
        else:
            [name, user_assembly, status, *_] = data + [None] * 100
            if status is None:
                status = request.user.is_authenticated

        self.user = request.user
        self.name = name
        self.user_assembly = user_assembly
        self.user_assembly_db_manager = UserAssemblyDBManager(user_assembly, self.user)

        if status != request.user.is_authenticated:
            self.session[settings.ASSEMBLY_SESSION_ID] = [name, user_assembly, self.user.is_authenticated]
            self.session.modified = True

            if request.user.is_authenticated:
                # logon performed. must combine assembly in db and assembly in session not to lose session assembly
                self.update_from_db()

    @classmethod
    def default_assembly_name(cls):
        return 'Сборка'

    def update_from_db(self):
        for component in self.user_assembly_db_manager:
            self.add(component.product, component.quantity)
            self.save()

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the assembly or update its quantity.
        """
        product_id = str(product.id)
        if product_id not in self.user_assembly:
            self.user_assembly[product_id] = {'quantity': 0,
                                              'price': str(product.price())}
        if override_quantity:
            self.user_assembly[product_id]['quantity'] = quantity
        else:
            self.user_assembly[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True
        self.user_assembly_db_manager.update()

    def remove(self, product):
        """
        Remove a product from the assembly.
        """
        product_id = str(product.id)

        if product_id in self.user_assembly:
            del self.user_assembly[product_id]
            self.save()

    def make_current(self, assembly):
        assert isinstance(assembly, Assembly)
        assert assembly.id

        UserAssemblyDBManager.set_default_assembly(user=self.user, assembly=assembly)

        self.name = assembly.name
        self.user_assembly = {}
        self.user_assembly_db_manager = UserAssemblyDBManager(self.user_assembly, self.user)
        self.update_from_db()

        self.session[settings.ASSEMBLY_SESSION_ID] = [self.name, self.user_assembly, self.user.is_authenticated]
        self.session.modified = True

    def __iter__(self):
        """
        Iterate over the products in the assembly and get the products
        from the database.
        """
        product_ids = self.user_assembly.keys()
        # get the product objects and add them to the assembly
        products = Product.objects.filter(id__in=product_ids)
        user_assembly = deepcopy(self.user_assembly)
        for product in products:
            user_assembly[str(product.id)]['product'] = product
        for item in user_assembly.values():
            try:
                item['price'] = Decimal(item['price'])
            except decimal.InvalidOperation:
                item['price'] = 0

            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count products in the assembly.
        """
        return len(self.user_assembly)

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.user_assembly.values())

    def clear(self):
        # remove assembly from session
        self.save()

    def get_id(self):
        return self.user_assembly_db_manager.assembly.id if self.user_assembly_db_manager.assembly else None


class UserAssemblyDBManager:
    def __init__(self, user_assembly, user):
        self.user = user
        self.assembly = self.get_or_create_assembly(user)
        self.user_assembly = user_assembly

    @classmethod
    def get_or_create_assembly(cls, user):
        assembly = None
        if user.is_authenticated:
            assembly = Assembly.objects.filter(default_for__user=user, owner=user).first()

            if not assembly:
                with transaction.atomic():
                    assembly = Assembly.objects.create(owner=user, name=UserAssembly.default_assembly_name())
                    cls.set_default_assembly(user=user, assembly=assembly)

        return assembly

    @classmethod
    def set_default_assembly(cls, user, assembly):
        profile_model = apps.get_model('account', 'Profile')

        profile = profile_model.objects.get(user=user)
        profile.default_assembly = assembly
        profile.save()

    def __iter__(self):
        if self.assembly:
            components = self.assembly.assemblycomponent_set.all().select_related('product')
            for component in components:
                yield component

    def update(self):
        if self.assembly:
            components = self.assembly.assemblycomponent_set.all().select_related('product')
            for component in components:
                if component.product.id in self.user_assembly:
                    if component.quantity != self.user_assembly[component.product.id].quantity:
                        component.quantity = self.user_assembly[component.product.id].quantity
                        component.save()
                else:
                    component.delete()

            for product_id in self.user_assembly:
                if product_id not in (component.product.id for component in components):
                    product = Product.objects.get(id=product_id)
                    AssemblyComponent.objects.create(assembly=self.assembly,
                                                     product=product,
                                                     quantity=self.user_assembly[product_id]['quantity'])

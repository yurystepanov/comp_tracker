from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator

from .models import Assembly
from .services import UserAssembly
from .forms import AssemblyTitleForm
from product.models import Product


# Create your views here.
class AssemblyListView(ListView):
    model = Assembly
    context_object_name = 'assemblies'
    template_name = 'assembly/assembly/list.html'
    allow_edit = False

    def get_queryset(self):
        qs = super().get_queryset()
        qs = self.add_owner_filter(qs)

        qs = qs.prefetch_related(Prefetch('component', queryset=Product.objects.order_by('group__order')))

        return qs

    def add_owner_filter(self, qs):
        qs = qs.filter(owner__isnull=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allow_edit'] = self.allow_edit

        form = AssemblyTitleForm()
        context['assembly_add_form'] = form

        context['current_assembly_id'] = UserAssembly(self.request).get_id()

        return context


@method_decorator(login_required, name='dispatch')
class UserAssemblyListView(AssemblyListView):
    allow_edit = True

    def add_owner_filter(self, qs):
        qs = qs.filter(owner=self.request.user)
        return qs


class AssemblyDetailView(DetailView):
    model = Assembly
    context_object_name = 'assembly'
    template_name = 'assembly/assembly/detail.html'


def user_assembly(request):
    assembly = UserAssembly(request)

    return render(request,
                  'assembly/assembly/user_assembly.html',
                  {'assembly_name': assembly.name,
                   'assembly': assembly,
                   })


@require_POST
@login_required
def edit_user_assembly(request):
    form = AssemblyTitleForm(data=request.POST)
    if form.is_valid():
        assembly = form.save(commit=False)
        assembly.owner = request.user
        assembly.save()

        return redirect('assembly:user_assembly_list')


@require_POST
def change_product_qty(request):
    if request.method == "POST":
        if request.POST.get("operation") == "change_product_qty":
            product_id = request.POST.get("product", None)
            quantity = int(request.POST.get("quantity", None))

            product = get_object_or_404(Product, id=product_id)

            assembly = UserAssembly(request)
            if quantity:
                assembly.add(product, quantity=quantity, override_quantity=True)
            else:
                assembly.remove(product)

            return JsonResponse({"quantity": quantity})


@require_POST
@login_required()
def current_assembly(request):
    if request.method == 'POST':
        assembly_id = request.POST.get('id', None)

        get_object_or_404(Assembly, id=assembly_id, owner=request.user)

        assembly = UserAssembly(request)
        assembly.make_current(assembly)

        return JsonResponse(data={})

from django_filters.constants import EMPTY_VALUES


class ExtraPredicateMixin:
    extra_predicate_name = ''
    extra_predicate_value = ''

    def set_extra_predicate(self, name, value):
        self.extra_predicate_name = name
        self.extra_predicate_value = value


class ExtraPredicateFilterMixin(ExtraPredicateMixin):
    def filter(self, qs, value):
        if value:
            if value.start is not None and value.stop is not None:
                self.lookup_expr = "range"
                value = (value.start, value.stop)
            elif value.start is not None:
                self.lookup_expr = "gte"
                value = value.start
            elif value.stop is not None:
                self.lookup_expr = "lte"
                value = value.stop

        if value in EMPTY_VALUES:
            return qs
        if self.distinct:
            qs = qs.distinct()
        lookup = "%s__%s" % (self.field_name, self.lookup_expr)
        predicates = {lookup: value}
        if self.extra_predicate_name:
            predicates[self.extra_predicate_name] = self.extra_predicate_value
        qs = self.get_method(qs)(**predicates)
        return qs


class ExtraPredicateMultipleChoiceMixin(ExtraPredicateMixin):
    def get_filter_predicate(self, v):
        predicates = super().get_filter_predicate(v)

        if predicates and self.extra_predicate_name:
            predicates[self.extra_predicate_name] = self.extra_predicate_value

        return predicates

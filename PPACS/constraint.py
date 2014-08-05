
#date
#year
#month
#day
#time
#hour
#minute
#second
import sys
import datetime
from Provider.models import Expression


class ConstraintChecker:
    RESERVED = ('year', 'month', 'day', 'hour', 'minute', 'second', 'day name', 'month name')

    class Error(Exception):
        pass

    class Constraint:

        def __str__(self):
            return '%s %s %s' % (self.variable, self.operator, self.value)

        def parse_set(self, value):
            striped = value.strip()
            if striped[0] != '{' or striped[-1] != '}':
                raise ValueError('set should start with { and end with }')
            striped = striped[1:-1]
            splited = striped.split(',')
            ret = set()

            for val in splited:
                striped = val.strip()
                if not striped:
                    continue
                ret.add(striped)
            return ret


        def __init__(self, variable, operator, value):
            if (operator, operator) not in Expression.OPERATOR_CHOICES:
                raise ConstraintChecker.Error("operator not supported in %s %s %s" % (variable, operator, value))
            self.variable = variable
            self.operator = operator

            if operator == Expression.HAS_MEMBER:
                self.value = str(value)
            elif operator in \
                (Expression.SUBSET, Expression.SUBSET_EQUAL, Expression.SUPERSET, Expression.SUPERSET_EQUAL, Expression.MEMBER):
                self.value = self.parse_set(value)
            else:
                try:
                    self.value = int(value)
                except ValueError:
                    try:
                        self.value = float(value)
                    except ValueError:
                        try:
                            self.value = self.parse_set(value)
                        except:
                            self.value = str(value)


    def __str__(self):
        ret = ""
        for x in self.environment.values():
            ret += '%s\n' % str(x)
        return ret

    class Rangable:


        def __str__(self):
            ret = ('%s %s:%s%s, %s%s-%s' % \
            (self.inferred, self.name, '[' if self.min_include else '(', self.range_min, self.range_max, ']' if self.max_include else ')', self.exclude))
            if self.include:
                if self.inferred is str:
                    ret += " in %s" % self.include
                elif self.inferred is set:
                    ret += " has %s" % self.include
            return ret

        def __init__(self, name):
            self.name = name
            self.range_max = None
            self.range_min = None
            self.max_include = False
            self.min_include = False
            self.inferred = None
            self.exclude = set()
            self.include = set()

        def check_range(self):
            if self.range_max is not None and self.range_min is not None:
                if (self.range_max < self.range_min) or \
                    (self.range_max == self.range_max and
                         (not self.max_include or not self.max_include or self.range_max in self.exclude)):
                    raise ConstraintChecker.Error("%s constraint range is not possible" % self.name)

                # special care for int
                if self.inferred is int:
                    start = self.range_min + 1
                    if self.min_include:
                        start -= 1
                    end = self.range_max - 1
                    if self.max_include:
                        end += 1
                    ok = False
                    for i in range(start, end+1):
                        if i not in self.exclude:
                            ok = True
                            break
                    if not ok:
                       raise ConstraintChecker.Error("%s all values in the possible range are excluded" % self.name)

                # special care for set
                if self.inferred is set:
                    if self.range_max is not None:
                        if self.include > self.range_max:
                            raise ConstraintChecker.Error("%s constraint range is not possible for this set" % self.name)

                # special care for string
                if self.inferred is str:
                    if self.include:
                        if self.range_max is not None:
                            if self.range_max not in self.include:
                                raise ConstraintChecker.Error("%s = %s but it should be in set %s" %
                                                              (self.name, self.range_max, str(self.include))
                                )


        def check_type(self, val, supported):
            if type(val) not in supported:
                raise ConstraintChecker.Error("operation not supported on inferred type of %s: %s" % (self.name, type(val)))
            if self.inferred is not None:
                if type(val) is not self.inferred:
                    raise ConstraintChecker.Error("%s inferred as %s but got %s" % (self.name, self.inferred, type(val)))
            else:
                self.inferred = type(val)

        def set_max(self, val, inclusive=False):
            supported = {int, float, set, str}
            self.check_type(val, supported)
            if self.range_max is None:
                self.range_max = val
                self.max_include = inclusive
            elif self.range_max == val:
                if not inclusive:
                    self.max_include = False
            elif self.range_max > val:
                self.range_max = val
                self.max_include = inclusive
            self.check_range()

        def set_min(self, val, inclusive=False):
            supported = {int, float, set, str}
            self.check_type(val, supported)
            if self.range_min is None:
                self.range_min = val
                self.min_include = inclusive
            elif self.range_min == val:
                if not inclusive:
                    self.min_include = False
            elif self.range_min < val:
                self.range_min = val
                self.min_include = inclusive
            self.check_range()

        def add_exclude(self, val):
            supported = {int, float, set, str}
            self.check_type(val, supported)
            if self.inferred is not set:
                self.exclude.add(val)
            #special care for set
            else:
                self.exclude.add(frozenset(val))
            self.check_range()

        def set_equal(self, val):
            supported = {int, float, set, str}
            self.set_min(val, inclusive=True)
            self.set_max(val, inclusive=True)
            # self.check_type(val, supported)
            # self.range_max = val
            # self.range_min = val
            # self.max_include = True
            # self.min_include = True
            # self.check_range()

        def add_member(self, val):
            supported = {set}
            self.check_type(set(), supported)
            if type(val) is not str:
                raise ConstraintChecker.Error("%s: only string sets are supported" % self.name)
            self.include.add(val)
            self.check_range()

        def is_member(self, val):
            supported = {str}
            self.check_type("", supported)
            if type(val) is not set:
                raise ConstraintChecker.Error("%s: only string sets are supported" % self.name)
            if self.include:
                self.include &= val
            else:
                self.include = val
            if not self.include:
                raise ConstraintChecker.Error("%s: constraint not satisfiable" % self.name)

            self.check_range()






    def __init__(self):
        self.environment = {}
        for x in ConstraintChecker.RESERVED:
            self.environment[x] = ConstraintChecker.Rangable(x)
        today = datetime.datetime.today()
        self.environment['year'].set_equal(today.year)
        self.environment['month'].set_equal(today.month)
        self.environment['day'].set_equal(today.day)
        self.environment['hour'].set_equal(today.hour)
        self.environment['minute'].set_equal(today.minute)
        self.environment['second'].set_equal(today.second)
        self.environment['day name'].is_member(set([
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ]))
        self.environment['month name'].is_member(set([
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]))


    def add_constraint(self, constraint):
        if constraint.variable not in self.environment:
            self.environment[constraint.variable] = ConstraintChecker.Rangable(constraint.variable)
        var = self.environment[constraint.variable]

        if constraint.operator == Expression.EQUAL:
            var.set_equal(constraint.value)
        elif constraint.operator == Expression.NOT_EQUAL:
            var.add_exclude(constraint.value)
        elif constraint.operator in (Expression.GREATER_EQUAL, Expression.SUPERSET_EQUAL):
            var.set_min(constraint.value, inclusive=True)
        elif constraint.operator in (Expression.GREATER, Expression.SUPERSET):
            var.set_min(constraint.value, inclusive=False)
        elif constraint.operator in (Expression.LESS_EQUAL, Expression.SUBSET_EQUAL):
            var.set_max(constraint.value, inclusive=True)
        elif constraint.operator in (Expression.LESS, Expression.SUBSET):
            var.set_max(constraint.value, inclusive=False)
        elif constraint.operator == Expression.MEMBER:
            var.is_member(constraint.value)
        elif constraint.operator == Expression.HAS_MEMBER:
            var.add_member(constraint.value)
        else:
            raise Exception('should not be here! %s %s %s' %
                            (constraint.variable, constraint.operator, constraint.value))
        print(self)




    def add_constraints(self, constraint_set):
        for constraint in constraint_set:
            print('adding %s' % str(constraint))
            self.add_constraint(constraint)





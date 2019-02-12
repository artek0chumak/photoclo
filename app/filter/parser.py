from yargy import rule, or_, Parser
from yargy.interpretation import fact
from yargy.predicates import normalized
from yargy.predicates import type as y_type

RelativeDate = fact('RelativeDate',
                    ['relDay', 'relWeek', 'relMonth', 'relYear'])

INT = y_type('INT')
day_rule = rule(INT.interpretation(RelativeDate.relDay),
                rule(normalized('день'))).interpretation(RelativeDate)
week_rule = rule(INT.interpretation(RelativeDate.relWeek),
                 rule(normalized('неделя'))).interpretation(RelativeDate)
month_rule = rule(INT.interpretation(RelativeDate.relMonth),
                  rule(normalized('месяц'))).interpretation(RelativeDate)
year_rule = rule(INT.interpretation(RelativeDate.relYear),
                 rule(or_(normalized('год'),
                          normalized('лет')))).interpretation(RelativeDate)

date_rule = rule(
    or_(day_rule, week_rule, month_rule, year_rule)
).interpretation(RelativeDate)

rel_date_parser = Parser(date_rule)

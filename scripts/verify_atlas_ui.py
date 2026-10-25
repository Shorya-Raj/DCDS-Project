"""UI regression checks for the Atlas layout using real local stores."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=30)
def clean(label):
    assert not app.exception, [(e.message) for e in app.exception]
    assert not app.error, [(e.value) for e in app.error]
    print('PASS', label)
def button(label):
    return next(b for b in app.button if b.label == label)
def select(label):
    return next(b for b in app.selectbox if b.label == label)
def radio(label):
    return next(b for b in app.radio if b.label == label)
app.run()
clean('database initial render')
assert app.metric[0].value == '1,572', app.metric[0].value
assert len([b for b in app.button if b.label == 'Inspect record']) == 6
buttons = [b for b in app.button if b.label == 'Inspect record']
expected = buttons[1].key.removeprefix('open_')
buttons[1].click().run()
clean('card selection')
assert select('Inspect a listing').value == expected
app.number_input[0].set_value(2).run()
clean('second page')
assert app.number_input[0].value == 2
app.text_input[0].set_value('pipeline').run()
clean('search resets pagination')
assert app.number_input[0].value == 1
assert 0 < int(app.metric[0].value.replace(',','')) < 1572
select('Sort records').select('Highest estimate').run()
clean('estimate sorting')
radio('Browse as').set_value('Table').run()
clean('table view')
assert len(app.dataframe) > 0
app.text_input[0].set_value('no_such_record_zyx987').run()
clean('empty search')
assert app.metric[0].value == '0'
app.text_input[0].set_value('').run()
app.multiselect[0].set_value([]).run()
clean('empty category selection')
assert app.metric[0].value == '0'
app.multiselect[0].set_value(app.multiselect[0].options).run()
button('Run SQL search').click().run()
clean('SQL query')
assert app.session_state['sql_result'][0]
button('Run MongoDB search').click().run()
clean('Mongo query')
assert app.session_state['mongo_result'][0]
radio('Data source').set_value('Sample data').run()
clean('sample fallback')
assert app.metric[0].value == '129'
radio('Browse as').set_value('Cards').run()
clean('sample cards')
radio('Data source').set_value('MySQL + MongoDB').run()
clean('return to database')
assert app.metric[0].value == '1,572'
print('ALL UI CHECKS PASSED')

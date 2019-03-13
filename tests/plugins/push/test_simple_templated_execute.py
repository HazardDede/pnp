import mock
import pytest

from pnp.plugins.push.simple import TemplatedExecute
from pnp.shared.exc import TemplateError


class MockedBufferedReader:
    def __init__(self, data):
        self.data = data
    def __iter__(self):
        return iter(self.data)
    def close(self):
        pass


@mock.patch('subprocess.Popen')
def test_execute_push(mock_popen):
    dut = TemplatedExecute(command="date", name='pytest')  # no args

    mock_popen.return_value.returncode = 0
    mock_popen.return_value.stdout = MockedBufferedReader(["2018-11-27"])
    mock_popen.return_value.stderr = MockedBufferedReader(["2018-11-28"])
    res = dut.push(None)  # no dict payload -> no templates -> no injection

    mock_popen.assert_called_with(args='date', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1, universal_newlines=True)
    assert isinstance(res, dict)
    assert {'return_code', 'stdout', 'stderr'} == set(res.keys())
    assert res['return_code'] == 0
    assert res['stdout'] == ["2018-11-27"]
    assert res['stderr'] == ["2018-11-28"]


@mock.patch('subprocess.Popen')
def test_execute_push_with_args(mock_popen):
    mock_popen.return_value.returncode = 0
    mock_popen.return_value.stdout = MockedBufferedReader(["hello", "you"])
    mock_popen.return_value.stderr = MockedBufferedReader([])

    dut = TemplatedExecute(command="echo", args='-e "hello\nyou"', name='pytest')
    res = dut.push(None)

    mock_popen.assert_called_with(args='echo "-e \\\"hello\nyou\\\""', cwd=dut.base_path, shell=True, stderr=-1,
                                  stdout=-1, universal_newlines=True)
    assert isinstance(res, dict)
    assert {'return_code', 'stdout', 'stderr'} == set(res.keys())
    assert res['return_code'] == 0
    assert res['stdout'] == ["hello", "you"]
    assert res['stderr'] == []

    dut = TemplatedExecute(command="echo", args=['-e', '"hello\nyou"'], name='pytest', cwd="/tmp")
    dut.push(None)
    mock_popen.assert_called_with(args='echo "-e" "\\\"hello\nyou\\\""', cwd="/tmp", shell=True, stderr=-1, stdout=-1,
                                  universal_newlines=True)


@mock.patch('subprocess.Popen')
def test_execute_push_without_args_but_payload(mock_popen):
    mock_popen.return_value.returncode = 0
    mock_popen.return_value.stdout = MockedBufferedReader(["2018-11-27"])
    mock_popen.return_value.stderr = MockedBufferedReader([])

    dut = TemplatedExecute(command="{{command}}", capture=True, name='pytest')
    res = dut.push(dict(command='date'))

    mock_popen.assert_called_with(args='date', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1, universal_newlines=True)
    assert isinstance(res, dict)
    assert {'return_code', 'stdout', 'stderr'} == set(res.keys())
    assert res['return_code'] == 0
    assert res['stdout'] == ["2018-11-27"]


@mock.patch('subprocess.Popen')
def test_execute_push_with_args_and_payload(mock_popen):
    mock_popen.return_value.returncode = 0
    mock_popen.return_value.stdout = MockedBufferedReader(["hello", "dude", "!"])
    mock_popen.return_value.stderr = MockedBufferedReader([])

    dut = TemplatedExecute(command="{{command}}", args=['hello', '{{name}}', '!'], capture=True, name='pytest')
    res = dut.push(dict(command='echo', name='dude'))

    mock_popen.assert_called_with(args='echo "hello" "dude" "!"', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1, universal_newlines=True)
    assert isinstance(res, dict)
    assert {'return_code', 'stdout', 'stderr'} == set(res.keys())
    assert res['return_code'] == 0
    assert res['stdout'] == ["hello", "dude", "!"]


@mock.patch('subprocess.Popen')
def test_execute_push_with_unknown_template_var(mock_popen):
    dut = TemplatedExecute(command="{{command}}", args=['hello', '{{name}}', '!'], capture=True, name='pytest')

    with pytest.raises(TemplateError) as e:
        dut.push(dict(command='echo'))
    assert "Error when rendering template in TemplatedExecute" in str(e)


@mock.patch('subprocess.Popen')
def test_execute_push_with_unused_template_var(mock_popen):
    dut = TemplatedExecute(command="{{command}}", args=['hello', '{{name}}', '!'], capture=True, name='pytest')

    dut.push(dict(command='echo', name="you", toomuch="I am not used"))
    mock_popen.assert_called_with(args='echo "hello" "you" "!"', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1,
                                  universal_newlines=True)


@mock.patch('subprocess.Popen')
def test_execute_push_with_dict_in_dict_referencing(mock_popen):
    dut = TemplatedExecute(command="{{command}}", args=['hello', '{{label.name}}', '!'], capture=True, name='pytest')

    dut.push(dict(command='echo', label=dict(name="you")))
    mock_popen.assert_called_with(args='echo "hello" "you" "!"', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1,
                                  universal_newlines=True)


@mock.patch('subprocess.Popen')
def test_execute_push_with_empty_and_none_args(mock_popen):
    dut = TemplatedExecute(command="{{command}}", args=['hello', '{{label.name}}', '!'], capture=True, name='pytest')

    dut.push(dict(command='echo', label=dict(name="")))
    mock_popen.assert_called_with(args='echo "hello" "!"', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1,
                                  universal_newlines=True)

    dut.push(dict(command='echo', label=dict(name=None)))
    mock_popen.assert_called_with(args='echo "hello" "!"', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1,
                                  universal_newlines=True)


@mock.patch('subprocess.Popen')
def test_execute_push_with_no_dict_as_args(mock_popen):
    dut = TemplatedExecute(command="echo", args=['hello', '{{payload}}', '!'], capture=True, name='pytest')

    dut.push("no dict")
    mock_popen.assert_called_with(args='echo "hello" "no dict" "!"', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1,
                                  universal_newlines=True)

from tempfile import TemporaryDirectory

import pytest

from pnp.exc import TemplateError
from pnp.plugins.push.simple import Execute


class MockedBufferedReader:
    def __init__(self, data):
        self.data = data
    def __iter__(self):
        return iter(self.data)
    def close(self):
        pass


@pytest.mark.asyncio
async def test_push_no_args(mocker):
    dut = Execute(command="date", name='pytest')  # no args

    mock_popen = mocker.patch('subprocess.Popen')
    mock_popen.return_value.returncode = 0
    mock_popen.return_value.stdout = MockedBufferedReader(["2018-11-27"])
    mock_popen.return_value.stderr = MockedBufferedReader(["2018-11-28"])
    res = await dut.push(None)  # no dict payload -> no templates -> no injection

    mock_popen.assert_called_with(args='date', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1, universal_newlines=True)
    assert isinstance(res, dict)
    assert {'return_code', 'stdout', 'stderr'} == set(res.keys())
    assert res['return_code'] == 0
    assert res['stdout'] == ["2018-11-27"]
    assert res['stderr'] == ["2018-11-28"]


@pytest.mark.asyncio
async def test_push_with_args(mocker):
    mock_popen = mocker.patch('subprocess.Popen')
    mock_popen.return_value.returncode = 0
    mock_popen.return_value.stdout = MockedBufferedReader(["hello", "you"])
    mock_popen.return_value.stderr = MockedBufferedReader([])

    dut = Execute(command="echo", args='-e "hello\nyou"', name='pytest')
    res = dut._push(None)

    mock_popen.assert_called_with(args='echo "-e \\\"hello\nyou\\\""', cwd=dut.base_path, shell=True, stderr=-1,
                                  stdout=-1, universal_newlines=True)
    assert isinstance(res, dict)
    assert {'return_code', 'stdout', 'stderr'} == set(res.keys())
    assert res['return_code'] == 0
    assert res['stdout'] == ["hello", "you"]
    assert res['stderr'] == []

    dut = Execute(command="echo", args=['-e', '"hello\nyou"'], name='pytest', cwd="/tmp")
    await dut.push(None)
    mock_popen.assert_called_with(args='echo "-e" "\\\"hello\nyou\\\""', cwd="/tmp", shell=True, stderr=-1, stdout=-1,
                                  universal_newlines=True)


@pytest.mark.asyncio
async def test_push_no_args_but_payload(mocker):
    mock_popen = mocker.patch('subprocess.Popen')
    mock_popen.return_value.returncode = 0
    mock_popen.return_value.stdout = MockedBufferedReader(["2018-11-27"])
    mock_popen.return_value.stderr = MockedBufferedReader([])

    dut = Execute(command="{{command}}", capture=True, name='pytest')
    res = await dut.push(dict(command='date'))

    mock_popen.assert_called_with(args='date', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1, universal_newlines=True)
    assert isinstance(res, dict)
    assert {'return_code', 'stdout', 'stderr'} == set(res.keys())
    assert res['return_code'] == 0
    assert res['stdout'] == ["2018-11-27"]


@pytest.mark.asyncio
async def test_push_with_args_and_payload(mocker):
    mock_popen = mocker.patch('subprocess.Popen')
    mock_popen.return_value.returncode = 0
    mock_popen.return_value.stdout = MockedBufferedReader(["hello", "dude", "!"])
    mock_popen.return_value.stderr = MockedBufferedReader([])

    dut = Execute(command="{{command}}", args=['hello', '{{name}}', '!'], capture=True, name='pytest')
    res = await dut.push(dict(command='echo', name='dude'))

    mock_popen.assert_called_with(args='echo "hello" "dude" "!"', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1, universal_newlines=True)
    assert isinstance(res, dict)
    assert {'return_code', 'stdout', 'stderr'} == set(res.keys())
    assert res['return_code'] == 0
    assert res['stdout'] == ["hello", "dude", "!"]


@pytest.mark.asyncio
async def test_push_with_unknown_template_var(mocker):
    dut = Execute(command="{{command}}", args=['hello', '{{name}}', '!'], capture=True, name='pytest')

    with pytest.raises(TemplateError) as e:
        await dut.push(dict(command='echo'))
    assert "Error when rendering template in TemplatedExecute" in str(e)


@pytest.mark.asyncio
async def test_push_with_unused_template_var(mocker):
    mock_popen = mocker.patch('subprocess.Popen')
    dut = Execute(command="{{command}}", args=['hello', '{{name}}', '!'], capture=True, name='pytest')

    await dut.push(dict(command='echo', name="you", toomuch="I am not used"))
    mock_popen.assert_called_with(args='echo "hello" "you" "!"', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1,
                                  universal_newlines=True)


@pytest.mark.asyncio
async def test_push_with_dict_in_dict_referencing(mocker):
    mock_popen = mocker.patch('subprocess.Popen')
    dut = Execute(command="{{command}}", args=['hello', '{{label.name}}', '!'], capture=True, name='pytest')

    await dut.push(dict(command='echo', label=dict(name="you")))
    mock_popen.assert_called_with(args='echo "hello" "you" "!"', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1,
                                  universal_newlines=True)


@pytest.mark.asyncio
async def test_push_with_empty_and_none_args(mocker):
    mock_popen = mocker.patch('subprocess.Popen')
    dut = Execute(command="{{command}}", args=['hello', '{{label.name}}', '!'], capture=True, name='pytest')

    await dut.push(dict(command='echo', label=dict(name="")))
    mock_popen.assert_called_with(args='echo "hello" "!"', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1,
                                  universal_newlines=True)

    await dut.push(dict(command='echo', label=dict(name=None)))
    mock_popen.assert_called_with(args='echo "hello" "!"', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1,
                                  universal_newlines=True)


@pytest.mark.asyncio
async def test_push_with_no_dict_as_args(mocker):
    mock_popen = mocker.patch('subprocess.Popen')
    dut = Execute(command="echo", args=['hello', '{{payload}}', '!'], capture=True, name='pytest')

    await dut.push("no dict")
    mock_popen.assert_called_with(args='echo "hello" "no dict" "!"', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1,
                                  universal_newlines=True)


def test_repr():
    with TemporaryDirectory() as tmpdir:
        dut = Execute(command="echo", args=['hello', '{{payload}}', '!'], capture=True, name='pytest', cwd=tmpdir)
        assert repr(dut) == (
            f"Execute(args=['hello', '{{{{payload}}}}', '!'], capture=True, command='echo', cwd='{tmpdir}', "
            f"name='pytest', timeout=5)"
        )

import mock

from pnp.plugins.push.simple import Execute


class MockedBufferedReader:
    def __init__(self, data):
        self.data = data
    def __iter__(self):
        return iter(self.data)
    def close(self):
        pass


@mock.patch('subprocess.Popen')
def test_execute_push(mock_popen):
    dut = Execute("date", name='pytest')

    mock_popen.return_value.returncode = 0
    mock_popen.return_value.stdout = MockedBufferedReader(["2018-11-27"])
    mock_popen.return_value.stderr = MockedBufferedReader(["2018-11-28"])
    res = dut.push({})

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

    dut = Execute("echo", args='-e "hello\nyou"', name='pytest')
    res = dut.push({})

    mock_popen.assert_called_with(args='echo -e "hello\nyou"', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1, universal_newlines=True)
    assert isinstance(res, dict)
    assert {'return_code', 'stdout', 'stderr'} == set(res.keys())
    assert res['return_code'] == 0
    assert res['stdout'] == ["hello", "you"]
    assert res['stderr'] == []

    dut = Execute("echo", args=['-e', '"hello\nyou"'], name='pytest', cwd="/tmp")
    dut.push({})
    mock_popen.assert_called_with(args='echo -e "hello\nyou"', cwd="/tmp", shell=True, stderr=-1, stdout=-1, universal_newlines=True)


@mock.patch('subprocess.Popen')
def test_execute_push_with_capture_off(mock_popen):
    dut = Execute("date", capture=False, name='pytest')

    mock_popen.return_value.returncode = 0
    res = dut.push({})

    mock_popen.assert_called_with(args='date', cwd=dut.base_path, shell=True, stderr=-1, stdout=-1, universal_newlines=True)
    assert isinstance(res, dict)
    assert {'return_code'} == set(res.keys())
    assert res['return_code'] == 0

from mock import patch

from pnp.plugins.push.notify import Pushbullet


@patch('pushbullet.Pushbullet')
def test_pushbullet_str_results_to_push_note(mock_pb):
    dut = Pushbullet(name='pytest', api_key='secret', title='pytest')
    dut._push("This is a string")

    mock_pb.assert_called
    mock_pb.return_value.push_note.assert_called
    mock_pb.return_value.push_note.assert_called_with('pytest', "This is a string")


@patch('pushbullet.Pushbullet')
def test_pushbullet_link_results_to_push_link(mock_pb):
    dut = Pushbullet(name='pytest', api_key='secret', title='pytest')
    dut._push("http://anyhost:1656/content?raw=1")

    mock_pb.assert_called
    mock_pb.return_value.push_link.assert_called
    mock_pb.return_value.push_link.assert_called_with('pytest', "http://anyhost:1656/content?raw=1")


@patch('pushbullet.Pushbullet')
def test_pushbullet_file_link_results_to_push_file(mock_pb):
    dut = Pushbullet(name='pytest', api_key='secret', title='pytest')
    dut._push("http://anyhost:1656/content.jpg?raw=1")

    mock_pb.assert_called
    mock_pb.return_value.push_file.assert_called
    mock_pb.return_value.push_file.assert_called_with(title='pytest', file_url='http://anyhost:1656/content.jpg?raw=1',
                                                      file_name='content.jpg', file_type='image/jpeg')

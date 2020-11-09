import io

from service.espnet import model


def test_read_vocab():
    v = model.Vocab(io.StringIO("a 1\nb 2\nc 3"))

    assert v.char_to_id["a"] == 1
    assert v.char_to_id["b"] == 2


def test_map_vocab():
    v = model.Vocab(io.StringIO("<unk> 1\n<space> 2\nc 3\nd 4"))

    assert v.map("d") == [4, 5]
    assert v.map("d d") == [4, 4, 5]
    assert v.map("c d") == [3, 4, 5]
    assert v.map("c d e") == [3, 4, 1, 5]
    assert v.map("c <space> d <space> e") == [3, 2, 4, 2, 1, 5]

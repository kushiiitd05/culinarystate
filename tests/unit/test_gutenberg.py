from culinarystate.ingest.gutenberg import book_dir, pick_file, strip_boilerplate


def test_book_dir():
    assert book_dir(10136).endswith("/1/0/1/3/10136/")
    assert book_dir(930).endswith("/9/3/930/") and book_dir(5).endswith("/0/5/")


def test_pick_file_prefers_utf8():
    html = '<a href="34107-8.txt">x</a><a href="34107.txt">y</a><a href="34107-0.txt">z</a>'
    assert pick_file(html, 34107) == ("34107-0.txt", "utf-8")
    assert pick_file(html + '<a href="34107-0.zip">', 34107) == ("34107-0.zip", "utf-8")
    assert pick_file('<a href="34107-8.txt">', 34107) == ("34107-8.txt", "latin-1")
    assert pick_file("", 1) is None


def test_strip_boilerplate():
    t = "header\n*** START OF THE PROJECT GUTENBERG EBOOK X ***\nBODY\n*** END OF THE PROJECT GUTENBERG EBOOK X ***\nlicence"
    assert strip_boilerplate(t) == "BODY"

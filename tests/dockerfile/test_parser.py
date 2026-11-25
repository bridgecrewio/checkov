from checkov.dockerfile.parser import convert_multiline_commands


def test_convert_multiline_commands_without_heredoc_unchanged():
    content = 'FROM python:3.12\nRUN pip install checkov\nCMD ["checkov"]'
    assert convert_multiline_commands(content) == content


def test_convert_multiline_commands_eof_heredoc():
    # the previously supported literal form keeps working
    content = (
        "FROM python:3.12\n"
        "RUN <<EOF\n"
        "pip install checkov\n"
        "pip install pytest\n"
        "EOF\n"
        'CMD ["checkov"]'
    )
    assert convert_multiline_commands(content) == (
        "FROM python:3.12\n"
        "RUN pip install checkov && pip install pytest\n"
        'CMD ["checkov"]'
    )


def test_convert_multiline_commands_custom_delimiter():
    # regression test for https://github.com/bridgecrewio/checkov/issues/7762
    # a heredoc with a non-EOF delimiter must be folded as well, otherwise its
    # body lines are parsed as Docker instructions
    content = (
        "FROM python:3.12\n"
        "RUN <<__user__\n"
        "groupadd --system app\n"
        "useradd --system --gid app --create-home --home-dir /home/app --shell /usr/sbin/nologin app\n"
        "__user__\n"
        'CMD ["app"]'
    )
    assert convert_multiline_commands(content) == (
        "FROM python:3.12\n"
        "RUN groupadd --system app && "
        "useradd --system --gid app --create-home --home-dir /home/app --shell /usr/sbin/nologin app\n"
        'CMD ["app"]'
    )


def test_convert_multiline_commands_dash_and_quoted_delimiters():
    assert convert_multiline_commands("RUN <<-EOT\necho hi\nEOT") == "RUN echo hi"
    assert convert_multiline_commands("RUN <<'EOT'\necho hi\nEOT") == "RUN echo hi"
    assert convert_multiline_commands('RUN <<"EOT"\necho hi\nEOT') == "RUN echo hi"


def test_convert_multiline_commands_multiple_heredocs_one_run():
    content = "RUN <<EOT1 <<EOT2\necho one\necho two\nEOT1\necho three\nEOT2"
    assert (
        convert_multiline_commands(content) == "RUN echo one && echo two && echo three"
    )


def test_convert_multiline_commands_sequential_heredocs():
    content = "RUN <<EOT1\necho one\nEOT1\nRUN <<EOT2\necho two\nEOT2"
    assert convert_multiline_commands(content) == "RUN echo one\nRUN echo two"


def test_convert_multiline_commands_run_without_heredoc_untouched():
    # '<<' later in the line is not a heredoc start for this folding
    content = 'RUN echo "a << b"'
    assert convert_multiline_commands(content) == content

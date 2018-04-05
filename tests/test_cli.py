import re
import warnings
import os

from lektor.cli import cli

def test_build_abort_in_existing_nonempty_dir(project_cli_runner):
    os.mkdir('build_dir')
    with open('build_dir/test', 'w'):
        pass
    result = project_cli_runner.invoke(cli, ["build", "-O", "build_dir"], input='n\n')
    assert "Aborted!" in result.output
    assert result.exit_code == 1


def test_build_continue_in_existing_nonempty_dir(project_cli_runner):
    os.mkdir('build_dir')
    with open('build_dir/test', 'w'):
        pass
    result = project_cli_runner.invoke(cli, ["build", "-O", "build_dir"], input='y\n')
    assert "Finished prune" in result.output
    assert result.exit_code == 0


def test_build_no_project(isolated_cli_runner):
    result = isolated_cli_runner.invoke(cli, ["build"])
    assert result.exit_code == 2
    assert "Could not automatically discover project." in result.output


def test_build(project_cli_runner):
    result = project_cli_runner.invoke(cli, ["build"])
    assert "files or folders already exist" not in result.output # No warning on fresh build
    assert result.exit_code == 0
    start_matches = re.findall(r"Started build", result.output)
    assert len(start_matches) == 1
    finish_matches = re.findall(r"Finished build in \d+\.\d{2} sec", result.output)
    assert len(finish_matches) == 1

    # rebuild
    result = project_cli_runner.invoke(cli, ["build"])
    assert "files or folders already exist" not in result.output # No warning on repeat build
    assert result.exit_code == 0


def test_build_extra_flag(project_cli_runner, mocker):
    mock_builder = mocker.patch('lektor.builder.Builder')
    mock_builder.return_value.build_all.return_value = 0
    result = project_cli_runner.invoke(cli, ["build", "-f", "webpack"])
    assert result.exit_code == 0
    assert mock_builder.call_args[1]["extra_flags"] == ("webpack",)
    assert 'use --extra-flag instead of --build-flag' not in result.output


def test_deprecated_build_flag(project_cli_runner, mocker):
    mock_builder = mocker.patch('lektor.builder.Builder')
    mock_builder.return_value.build_all.return_value = 0
    with warnings.catch_warnings(record=True) as w:
        result = project_cli_runner.invoke(cli, ["build", "--build-flag", "webpack"])
        assert result.exit_code == 0
        assert mock_builder.call_args[1]["extra_flags"] == ("webpack",)
        assert len(w) == 1
        assert 'use --extra-flag instead of --build-flag' in str(w[0].message)


def test_deploy_extra_flag(project_cli_runner, mocker):
    mock_publish = mocker.patch('lektor.publisher.publish')
    result = project_cli_runner.invoke(cli, ["deploy", "-f", "draft"])
    assert result.exit_code == 0
    assert mock_publish.call_args[1]["extra_flags"] == ("draft",)

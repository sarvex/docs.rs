from __future__ import print_function
import yaml
import sys
import os


def main():
    parent = f'scope:source.shell.{os.path.splitext(sys.argv[1])[0].split("-")[-1]}#'
    with open(sys.argv[1], "r") as stream:
        commands_input = yaml.load(stream)
    main = []
    main_bt = []
    contexts = {"main": main, "main-bt": main_bt}
    eoo = {
        "match": r"(?:\s+|^)--(?=\s|$)",
        "scope": r"keyword.operator.end-of-options.shell",
        "set": [
            {"meta_content_scope": r"meta.function-call.arguments.shell"},
            {"include": f"{parent}expansion-and-string"},
            {"include": f"{parent}line-continuation-or-pop-at-end"},
        ],
    }
    opt_end_boundary = r"(?=\s|;|$|`|\))"
    for command, value in commands_input.items():
        if not value:
            value = {}
        match = value.get("match", None)
        short_options = value.get("short-options", None)
        long_options = value.get("long-options", None)
        short_option_prefixes = value.get("short-option-prefixes", None)
        short_options_compact = value.get("short-options-compact", None)
        allow_eoo = value.get("allow-end-of-options-token", True)
        scope = value.get("scope", None)
        if not scope:
            scope = f"support.function.{command}.shell"
        scope = f"meta.function-call.shell {scope}"
        cmd_args_base = []
        cmd_args = []
        cmd_args_bt = []
        if match:
            match = "{{boundary_begin}}%s{{boundary_end}}" % match
        else:
            match = "{{boundary_begin}}%s{{boundary_end}}" % command
        if allow_eoo:
            cmd_args_base.append(eoo)
        if long_options:
            thedict = {
                "match": r"(?:\s+|^)((--)" + "|".join(long_options)
                                           + r")"
                                           + opt_end_boundary,
                "captures": {
                    2: "punctuation.definition.parameter.shell",
                    1: "variable.parameter.option.shell"
                }
            }
            cmd_args_base.append(thedict)
        thedict = {}
        thelist = []
        opts = ""
        if short_options:
            opts += f"[{short_options}]"
        if short_options_compact:
            if opts:
                opts += "|"
            opts += f"[{short_options_compact}" + "]+"
        if opts:
            if short_option_prefixes:
                prefix = "|".join(short_option_prefixes)
                thedict = {
                        "match": r"(?:\s+|^)((" + prefix
                                                + r")(?:"
                                                + opts
                                                + r"))"
                                                + opt_end_boundary,
                        "captures": {
                            2: "punctuation.definition.parameter.shell",
                            1: "variable.parameter.option.shell"
                        }
                    }
            else:
                thedict = {
                    "match": r"(?:\s+|^)((-)" + opts + r")" + opt_end_boundary,
                    "captures": {
                        2: "punctuation.definition.parameter.shell",
                        1: "variable.parameter.option.shell"
                    }
                }
        if thedict:
            cmd_args_base.append(thedict)
        if thelist:
            cmd_args_base.extend(thelist)
        cmd_args.extend(
            (
                {"meta_scope": "meta.function-call.arguments.shell"},
                {"include": parent + r"cmd-args-boilerplate"},
            )
        )
        cmd_args_bt.extend(
            (
                {"meta_scope": "meta.function-call.arguments.shell"},
                {"include": parent + r"cmd-args-boilerplate-bt"},
            )
        )
        if cmd_args_base:
            cmd_args.append({"include": f"cmd-args-{command}-base"})
            cmd_args_bt.append({"include": f"cmd-args-{command}-base"})
            contexts[f"cmd-args-{command}-base"] = cmd_args_base
        cmd_args = [{"match": "", "set": cmd_args}]
        cmd_args_bt = [{"match": "", "set": cmd_args_bt}]
        contexts[f"cmd-args-{command}"] = cmd_args
        contexts[f"cmd-args-{command}-bt"] = cmd_args_bt
        main.append(
            {
                "match": match,
                "scope": scope,
                "set": [f"{parent}cmd-post", f"cmd-args-{command}"],
            }
        )
        main_bt.append(
            {
                "match": match,
                "scope": scope,
                "set": [f"{parent}cmd-post", f"cmd-args-{command}-bt"],
            }
        )
    contexts["prototype"] = [{
        "include": parent + r"prototype"
    }]

    commands_output = {
        "scope": os.path.splitext(sys.argv[1])[0].replace("-", "."),
        "hidden": True,
        "variables": {
            "boundary_end": r"(?=\s|;|$|>|<|\|)",
            "boundary_begin": ''
        },
        "contexts": contexts
    }

    with open(sys.argv[2], "w") as stream:
        print("%YAML 1.2\n---", file=stream)
        print("# Automatically generated file -- do not edit!", file=stream)
        noalias_dumper = yaml.dumper.SafeDumper
        noalias_dumper.ignore_aliases = lambda self, data: True
        yaml.dump(commands_output,
                  stream,
                  default_flow_style=False,
                  allow_unicode=True,
                  default_style='',
                  Dumper=noalias_dumper)

    return 0


if __name__ == '__main__':
    exit(main())

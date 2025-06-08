def format_log(log_lines, result_label="Result", result_value=None):
    """
    Formatiert eine Logliste im CLI-Stil und hängt optional ein Ergebnis an.
    """
    lines = [f"> {line}" for line in log_lines]

    if result_value is not None:
        lines += ["", f"[{result_label}]", str(result_value)]

    return "\n".join(lines)

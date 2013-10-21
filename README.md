This parser source is here for studying and hacking.

If you're trying to write more syntax, I propose you call this in another window:

    watch "python main.py"

It lets you see the output of the 'input' -file, while you're working on the source. That way you stay on track what you're changing. Just be sure you don't hang it, the timestamp on the output stops ticking if you do though, so it is easy to detect.

You can check at the `lexemes` to get idea of which lexemes the tokenizer is reading. 

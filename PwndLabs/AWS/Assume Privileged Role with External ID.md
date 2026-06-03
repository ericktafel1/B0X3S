`52.0.51.234`

`AssumeRole` is similar to `sudo`

We find the email address `info@hugelogistics.com` and infer the domain name for the website is `hugelogistics.com`
	Update `/etc/hosts`
No buckets exposed when we inspect the source code, so we `ffuf` and `fer`
```bash
ffuf -c -w `fzf-wordlists` -u "http://hugelogistics.com/FUZZ" -e .conf,.txt,.json,.xml,.yaml,.yml,.env -mc 200,301 2>/dev/null
```
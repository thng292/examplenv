# examplenv
Utilities to generate example.env and merge them

## How to install

```bash
uv add https://github.com/thng292/examplenv
```

## Demo
### Gen example env
```bash
$ cat .env
# It retain whitespace and comment
VAR1=DoNotCommitYourEnv

VAR2=ButThisIsNotVerySecret
$ cat .env.test
STAGE=DEV
# It cut your secret out too. By putting !SECRET in the comment
OPENAI_API_KEY=sk-ldfkjslfjldsjflsd # !SECRET
$ uv run examplenv gen-example-env
Searching for .env files in: /workspaces/examplenv

Found 2 .env file(s):

Processing: /workspaces/examplenv/.env
  ✓ Generated: example.env

Processing: /workspaces/examplenv/.env.test
  ✓ Generated: example.env.test

Done!
$ cat example.env
# Example environment variables for .env
# It retain whitespace and comment
VAR1=DoNotCommitYourEnv

VAR2=ButThisIsNotVerySecret
$ cat example.env.test
# Example environment variables for .env.test
STAGE=DEV
# It cut your secret out too. By putting !SECRET in the comment
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY> # !SECRET
```
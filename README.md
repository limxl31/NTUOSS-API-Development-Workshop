## Introducton to API Development (Part 2)

### Virtual Environment Setup

#### MacOS & Linux

```console
$ python3 -m venv env 
$ source env/bin/activate
$ pip install -r requirements.txt
```

#### Windows

```console
> pip install virtualenv 
> virtualenv env
> pip install -r requirements.txt
```

### Run Live Server
> Run the Uvicorn live server to serve the API

```console
$ uvicorn main:app --reload
```

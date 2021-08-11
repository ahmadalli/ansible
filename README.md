**this repo doesn't have an stable release yet and variables might change in new minor versions**

# Common Ansible Collection


## Dependencies

### Python and Ansible

- python 3 is required
- ansible 4 is not supported
- jinja2 2.11+ is required

```
ansible<4.0.0,>=2.10.0
jinja2>=2.11.0
```

### Ansible Galaxy Roles

```yaml
roles:
  - src: geerlingguy.mysql
  - src: geerlingguy.pip
collections:
```

## Assumptions

the roles in this collection assume that the private ip would be defined on `ip` variable of each host, if necessary.

## Roadmap

- decouple this repo into different collections and roles
- add retry to tasks which are retriable
- add tags
- add proper documentations
- test before deploy on tags
- use namespaces for all modules

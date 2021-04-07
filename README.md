**this repo doesn't have an stable release yet and variables might change in new minor versions**

# Common Ansible Collection


## Dependencies

since python 2 is deprecated, only python 3 is supported

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

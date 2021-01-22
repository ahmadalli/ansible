**this repo doesn't have an stable release yet and variables might change in new minor versions**

# Common Ansible Collection


## Dependencies

```yaml
roles:
  - src: geerlingguy.mysql
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

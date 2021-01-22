**this repo doesn't have an stable release yet and variables might change in new minor versions**

# Common Ansible Collection


## Dependencies

```yaml
roles:
  - src: geerlingguy.mysql
collections:
```

## Roadmap

- decouple this repo into different collections of roles
- add retry to tasks which are retriable
- add tags
- add proper documentations
- test before deploy on tags

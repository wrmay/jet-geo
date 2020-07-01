# MAKING AN IMAGE AVAILABLE ON OPENSHIFT

```bash
oc new-build --binary=true --context-dir=./jet --name=jet
oc start-build jet --from-dir=./jet
```

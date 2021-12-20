import kopf
import kubernetes
import yaml
import os

@kopf.on.create('primed.io', 'v1', 'ephemeralvolumeclaims')
def create_fn(meta, body, spec, namespace, logger, **kwargs):

    name = meta.get('name')
    size = spec.get('size')
    if not size:
        raise kopf.HandlerFatalError(f"Size must be set. Got {size!r}.")

    path = os.path.join(os.path.dirname(__file__), './manifest/pvc.yaml')
    tmpl = open(path, 'rt').read()
    text = tmpl.format(name=name, size=size)
    data = yaml.safe_load(text)

    kopf.adopt(data, owner=body)

    api = kubernetes.client.CoreV1Api()
    obj = api.create_namespaced_persistent_volume_claim(
        namespace=namespace,
        body=data,
    )

    logger.info(f"PVC child is created: %s", obj)

    return {'pvc-name': obj.metadata.name}


@kopf.on.update('primed.io', 'v1', 'ephemeralvolumeclaims')
def update_fn(spec, status, namespace, logger, **kwargs):

    size = spec.get('size', None)
    if not size:
        raise kopf.HandlerFatalError(f"Size must be set. Got {size!r}.")

    pvc_name = status['create_fn']['pvc-name']
    pvc_patch = {'spec': {'resources': {'requests': {'storage': size}}}}

    api = kubernetes.client.CoreV1Api()
    obj = api.patch_namespaced_persistent_volume_claim(
        namespace=namespace,
        name=pvc_name,
        body=pvc_patch,
    )

    logger.info(f"PVC child is updated: %s", obj)


@kopf.on.field('primed.io', 'v1', 'ephemeralvolumeclaims', field='metadata.labels')
def relabel(old, new, status, namespace, logger, **kwargs):

    pvc_name = status['create_fn']['pvc-name']
    pvc_patch = {'metadata': {'labels': new}}

    api = kubernetes.client.CoreV1Api()
    obj = api.patch_namespaced_persistent_volume_claim(
        namespace=namespace,
        name=pvc_name,
        body=pvc_patch,
    )

    logger.info(f"PVC child labels are updated: %s", obj)

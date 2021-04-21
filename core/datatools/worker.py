import mis.worker
import core.models


def load_worker(worker_mis_id: int):
    mis_worker = mis.worker.Worker.get(worker_mis_id)
    worker, created = core.models.Worker.objects.get_or_create(
        last_name=mis_worker.last_name,
        first_name=mis_worker.first_name,
        birth=mis_worker.birth,
        middle_name=mis_worker.middle_name,
        defaults={
            'gender': mis_worker.gender
        }
    )
    if not created:
        worker.gender = mis_worker.gender
        worker.save()
    worker_org, created = core.models.WorkerOrganization.objects.get_or_create(
        worker=worker,
        org_id=mis_worker.org.id,
        mis_id=mis_worker.id,
        defaults={
            'post': mis_worker.post,
            'shop': mis_worker.shop
        }
    )
    if not created:
        worker_org.post = mis_worker.post
        worker_org.shop = mis_worker.shop
        worker_org.save()
    worker_org.save()
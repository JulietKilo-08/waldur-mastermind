from django.db import models
from django.utils.translation import gettext_lazy as _
from libcloud.compute.drivers.ec2 import REGION_DETAILS

from waldur_core.core.fields import JSONField
from waldur_core.core.models import RuntimeStateMixin
from waldur_core.structure import models as structure_models
from waldur_geo_ip.utils import get_coordinates_by_ip


class Region(structure_models.GeneralServiceProperty):
    class Meta:
        ordering = ['name']

    @classmethod
    def get_url_name(cls):
        return 'aws-region'


class Image(structure_models.GeneralServiceProperty):
    class Meta:
        ordering = ['name']

    region = models.ForeignKey(on_delete=models.CASCADE, to=Region)

    def __str__(self):
        return f'{self.name} | {self.region.name}'

    @classmethod
    def get_url_name(cls):
        return 'aws-image'

    @classmethod
    def get_backend_fields(cls):
        return super().get_backend_fields() + ('region',)


class Size(structure_models.GeneralServiceProperty):
    class Meta:
        ordering = ['cores', 'ram']

    regions = models.ManyToManyField(Region)
    cores = models.PositiveSmallIntegerField(help_text=_('Number of cores in a VM'))
    ram = models.PositiveIntegerField(help_text=_('Memory size in MiB'))
    disk = models.PositiveIntegerField(help_text=_('Disk size in MiB'))
    price = models.DecimalField(
        _('Hourly price rate'), default=0, max_digits=11, decimal_places=5
    )

    @classmethod
    def get_url_name(cls):
        return 'aws-size'

    @classmethod
    def get_backend_fields(cls):
        return super().get_backend_fields() + (
            'cores',
            'ram',
            'disk',
            'price',
            'regions',
        )


class Instance(structure_models.VirtualMachine):
    region = models.ForeignKey(on_delete=models.CASCADE, to=Region)
    public_ips = JSONField(
        default=list, help_text=_('List of public IP addresses'), blank=True
    )
    private_ips = JSONField(
        default=list, help_text=_('List of private IP addresses'), blank=True
    )
    size_backend_id = models.CharField(max_length=150, blank=True)

    @property
    def external_ips(self):
        return self.public_ips

    @property
    def internal_ips(self):
        return self.private_ips

    def detect_coordinates(self):
        if self.external_ips:
            return get_coordinates_by_ip(self.external_ips[0])
        region = self.region.backend_id
        endpoint = REGION_DETAILS[region]['endpoint']
        return get_coordinates_by_ip(endpoint)

    @classmethod
    def get_url_name(cls):
        return 'aws-instance'

    @classmethod
    def get_backend_fields(cls):
        return super().get_backend_fields() + ('runtime_state',)

    @classmethod
    def get_online_state(cls):
        return 'running'

    @classmethod
    def get_offline_state(cls):
        return 'stopped'


class Volume(RuntimeStateMixin, structure_models.BaseResource):
    VOLUME_TYPES = (
        ('gp2', _('General Purpose SSD')),
        ('io1', _('Provisioned IOPS SSD')),
        ('standard', _('Magnetic volumes')),
    )
    size = models.PositiveIntegerField(help_text=_('Size of volume in gigabytes'))
    region = models.ForeignKey(on_delete=models.CASCADE, to=Region)
    volume_type = models.CharField(max_length=8, choices=VOLUME_TYPES)
    device = models.CharField(max_length=128, blank=True, null=True)
    instance = models.ForeignKey(
        on_delete=models.CASCADE, to=Instance, blank=True, null=True
    )

    @classmethod
    def get_url_name(cls):
        return 'aws-volume'

    @classmethod
    def get_backend_fields(cls):
        return super().get_backend_fields() + (
            'name',
            'device',
            'size',
            'volume_type',
            'runtime_state',
        )

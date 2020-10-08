import pytest

from unit.applications.lang.python import TestApplicationPython
from unit.feature.isolation import TestFeatureIsolation


class TestPythonIsolation(TestApplicationPython):
    prerequisites = {'modules': {'python': 'any'}}

    def test_python_isolation_chroot(self, is_su):
        if not is_su:
            pytest.skip('requires root')

        isolation = {
            'rootfs': self.temp_dir,
        }

        self.load('empty', isolation=isolation)

        assert self.get()['status'] == 200, 'python chroot'

        self.load('ns_inspect', isolation=isolation)

        assert (
            self.getjson(url='/?path=' + self.temp_dir)['body']['FileExists']
            == False
        ), 'temp_dir does not exists in rootfs'

        assert (
            self.getjson(url='/?path=/proc/self')['body']['FileExists']
            == False
        ), 'no /proc/self'

        assert (
            self.getjson(url='/?path=/dev/pts')['body']['FileExists'] == False
        ), 'no /dev/pts'

        assert (
            self.getjson(url='/?path=/sys/kernel')['body']['FileExists']
            == False
        ), 'no /sys/kernel'

        ret = self.getjson(url='/?path=/app/python/ns_inspect')

        assert (
            ret['body']['FileExists'] == True
        ), 'application exists in rootfs'

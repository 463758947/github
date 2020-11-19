import shutil

import pytest

from conftest import option
from conftest import unit_run
from conftest import unit_stop
from unit.applications.lang.ruby import TestApplicationRuby
from unit.feature.isolation import TestFeatureIsolation


class TestRubyIsolation(TestApplicationRuby):
    prerequisites = {'modules': {'ruby': 'any'}, 'features': ['isolation']}

    @classmethod
    def setup_class(cls, complete_check=True):
        check = super().setup_class(complete_check=False)

        unit = unit_run()
        option.temp_dir = unit['temp_dir']

        TestFeatureIsolation().check(option.available, unit['temp_dir'])

        assert unit_stop() is None
        shutil.rmtree(unit['temp_dir'])

        return check if not complete_check else check()

    def test_ruby_isolation_rootfs_mount_namespace(self, is_su):
        isolation_features = option.available['features']['isolation'].keys()

        if not is_su:
            if not 'unprivileged_userns_clone' in isolation_features:
                pytest.skip('requires unprivileged userns or root')

            if 'user' not in isolation_features:
                pytest.skip('user namespace is not supported')

            if 'mnt' not in isolation_features:
                pytest.skip('mnt namespace is not supported')

            if 'pid' not in isolation_features:
                pytest.skip('pid namespace is not supported')

        isolation = {'rootfs': option.test_dir}

        if not is_su:
            isolation['namespaces'] = {
                'mount': True,
                'credential': True,
                'pid': True
            }

        self.load('status_int', isolation=isolation)

        assert 'success' in self.conf(
            '"/ruby/status_int/config.ru"', 'applications/status_int/script',
        )

        assert 'success' in self.conf(
            '"/ruby/status_int"', 'applications/status_int/working_directory',
        )

        assert self.get()['status'] == 200, 'status int'

    def test_ruby_isolation_rootfs(self, is_su):
        if not is_su:
            pytest.skip('requires root')
            return

        isolation = {'rootfs': option.test_dir}

        self.load('status_int', isolation=isolation)

        assert 'success' in self.conf(
            '"/ruby/status_int/config.ru"', 'applications/status_int/script',
        )

        assert 'success' in self.conf(
            '"/ruby/status_int"', 'applications/status_int/working_directory',
        )

        assert self.get()['status'] == 200, 'status int'

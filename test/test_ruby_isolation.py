
import pytest

from conftest import option
from unit.applications.lang.ruby import TestApplicationRuby
from unit.feature.isolation import TestFeatureIsolation


class TestRubyIsolation(TestApplicationRuby):
    prerequisites = {'modules': {'ruby': 'any'}, 'features': ['isolation']}

    isolation = TestFeatureIsolation()

    @classmethod
    def setup_class(cls, complete_check=True):
        unit = super().setup_class(complete_check=False)

        TestFeatureIsolation().check(cls.available, unit.temp_dir)

        return unit if not complete_check else unit.complete()

    def test_ruby_isolation_rootfs(self, is_su):
        isolation_features = self.available['features']['isolation'].keys()

        if 'mnt' not in isolation_features:
            pytest.skip('requires mnt ns')

        if not is_su:
            if 'user' not in isolation_features:
                pytest.skip('requires unprivileged userns or root')

            if not 'unprivileged_userns_clone' in isolation_features:
                pytest.skip('requires unprivileged userns or root')

        isolation = {
            'namespaces': {'credential': not is_su, 'mount': True},
            'rootfs': option.test_dir,
        }

        self.load('status_int', isolation=isolation)

        assert 'success' in self.conf(
            '"/ruby/status_int/config.ru"', 'applications/status_int/script',
        )

        assert 'success' in self.conf(
            '"/ruby/status_int"', 'applications/status_int/working_directory',
        )

        assert self.get()['status'] == 200, 'status int'

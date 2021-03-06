import os.path
import shutil
from tempfile import mkdtemp
from unittest import TestCase

import pytest

from drupy.objects import DrupalOrgProject, UrllibDownloader, TarballExtract


class DrupalOrgProjectTest(TestCase):

    def test_split_project(self):
        assert DrupalOrgProject.split_project('campaignion-7.x-1.5+pr32') == \
            ('campaignion', '7.x', '1.5', ('pr32', ))
        assert DrupalOrgProject.split_project('campaignion-7.x-1.0-rc1') == \
            ('campaignion', '7.x', '1.0-rc1', tuple())
        assert DrupalOrgProject.split_project('campaignion-7.x-1.x-dev') == \
            ('campaignion', '7.x', '1.x-dev', tuple())
        with pytest.raises(ValueError) as e:
            DrupalOrgProject.split_project('sentry-php-1.6.2')

    def test_is_valid(self):
        # Valid package spec without declaring type.
        p = DrupalOrgProject(None, dict(dirname='campaignion-7.x-1.0'))
        assert p.isValid()

        # Invalid package spec but declaring type.
        p = DrupalOrgProject(None, dict(
            dirname='testitt',
            build=[{}],
            type='drupal.org',
        ))
        assert p.isValid()

        # Invalid package spec without declaring type.
        p = DrupalOrgProject(None, dict(dirname='testitt'))
        assert not p.isValid()


class TarballExtractTest(TestCase):

    def setup_method(self, test_method):
        self.testdir = mkdtemp()

    def teardown_method(self, test_method):
        shutil.rmtree(self.testdir)

    def test_libraries(self):
        """ Test whether the top-level directory is properly stripped. """
        class Fakerunner:
            class options:
                verbose = False
        dl = UrllibDownloader(Fakerunner, config=dict(
            url='https://ftp.drupal.org/files/projects/libraries-7.x-2.3.tar.gz'
        ))
        ex = TarballExtract(Fakerunner, config=dict(
            localpath = dl.download('', self.testdir).localpath()
        ))
        ex.applyTo(self.testdir + '/libraries')
        os.path.exists(self.testdir + '/libraries/libraries.module')

    def test_highcharts(self):
        """ Highcharts is a zip-file without any directories to strip. """
        class Fakerunner:
            class options:
                verbose = False
        dl = UrllibDownloader(Fakerunner, config=dict(
            url='http://code.highcharts.com/zips/Highcharts-4.2.7.zip'
        ))
        ex = TarballExtract(Fakerunner, config=dict(
            localpath = dl.download('', self.testdir).localpath()
        ))
        ex.applyTo(self.testdir + '/highcharts')
        os.path.exists(self.testdir + '/highcharts/js/highcharts.js')

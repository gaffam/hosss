import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from musica.project_manager import ProjectManager
from musica.cloud_sync import CloudSync


def test_cloud_push_pull(tmp_path):
    pm = ProjectManager(directory=tmp_path / 'local')
    cloud_dir = tmp_path / 'cloud'
    sync = CloudSync(pm, directory=str(cloud_dir))
    data = {'foo': 1}
    sync.push('proj', data)
    pm2 = ProjectManager(directory=tmp_path / 'local2')
    sync2 = CloudSync(pm2, directory=str(cloud_dir))
    pulled = sync2.pull('proj')
    assert pulled == data
    assert os.path.exists(pm2.save('proj', pulled))

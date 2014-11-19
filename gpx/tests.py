'''
Test Harness for Database Operations

@author: Brian O'Hare
'''

from django.test import TestCase
from datetime import datetime
from string import Template
from gpx import gpx_proc


class TestGPXProc(TestCase):
    
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
        """
        # ogr commands
        self.ogr_commands = {}
        for layer in layers:
            cmd = Template('ogr2ogr -f $driver $output_file PG:\"user=$user dbname=$dbname\" -lco RESIZE=yes -sql $sql -a_srs EPSG:27700 -preserve_fid -fieldTypeToString StringList"')
            ogr_args = cmd.safe_substitute({'driver':'SHP','output_file':'text.shp','user':'dbuser',
                            'dbname':'osmm','sql': '"select get_ads_vectors();FETCH ALL IN cursor;"'})
            self.ogr_commands[layer] = ogr_args
        self.audit_info.results['ogr_commands'] = self.ogr_commands
        """     
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    
      
            
    
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()



        



# Create your tests here.

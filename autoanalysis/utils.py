import sys
import logging
from glob import iglob
from hashlib import sha256
from os import access, R_OK
from os.path import join, abspath, dirname, split


def generateuid(seriesnum):
    hashed = sha256(str(seriesnum).encode('utf-8')).hexdigest()
    return hashed


def checkhashed(seriesnum, hashed):
    if hashed == sha256(str(seriesnum).encode('utf-8')).hexdigest():
        print("It Matches!")
        return True
    else:
        print("It Does not Match")
        return False

##### Global functions
def findResourceDir():
    # try local
    if sys.platform =='darwin':
        resource_dir = join('.','autoanalysis', 'resources')
    else:
        resource_dir = join('autoanalysis','resources')
    if not access(resource_dir,R_OK):
        #print('1b. Cannot access local resource_dir')
        #Try to locate resource dir
        base = dirname(abspath('.'))
        allfiles = [y for y in iglob(join(base,'**', "resources"))]#, recursive=True)]
        files = [f for f in allfiles if not 'build' in f]
        #print('Possible paths: ', len(files))
        if len(files) == 1:
            resource_dir = files[0]
            #print('2. Found resources at: ', abspath(resource_dir))
        elif len(files) > 1:
            for rf in files:
                if access(rf, R_OK):
                    resource_dir= rf
                    #print('3. Access resources at ', abspath(rf))
                    break
        else:
            raise ValueError('Cannot locate resources dir: ', abspath(resource_dir))
    msg ='Resources dir located to: %s' % abspath(resource_dir)
    print(msg)
    logging.debug(msg)
    return abspath(resource_dir)

def CheckFilenames(filenames, configfiles):
    """
    Check that filenames are appropriate for the script required
    :param filenames: list of full path filenames
    :param configfiles: matching filename for script as in config
    :return: filtered list
    """
    newfiles = {k: [] for k in filenames.keys()}
    for conf in configfiles:
        # if conf.startswith('_'):
        #     conf = conf[1:]
        for group in filenames.keys():
            for f in filenames[group]:
                parts = split(f)
                if conf in parts[1] or conf[1:] in parts[1]:
                    newfiles[group].append(f)
                elif conf.startswith('_'):
                    c = conf[1:]
                    newfiles[group] = newfiles[group] + [y for y in
                                                         iglob(join(parts[0], '**', '*' + c), recursive=True)]
                else:
                    # extract directory and seek files
                    newfiles[group] = newfiles[group] + [y for y in iglob(join(parts[0], '**', conf), recursive=True)]

    # if self.filesIn is not None:
    #     checkedfilenames = CheckFilenames(self.filenames, self.filesIn)
    #     files = [f for f in checkedfilenames if self.controller.datafile in f]
    # else:
    #     files = self.filenames
    return newfiles



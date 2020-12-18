# Copyright 2020 The AmpliGraph Authors. All Rights Reserved.
#
# This file is Licensed under the Apache License, Version 2.0.
# A copy of the Licence is available in LICENCE, or at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
"""Data source identifier.

This module provides main class and supporting functions for automatic
identification of data source (whether it is csv, tar.gz or numpy array)
and provides adequate loader for the data source identified.
"""
import pandas as pd
from collections.abc import Iterable
import numpy as np
from itertools import chain, islice
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def load_csv(data_source, chunk_size=None, sep='\t', verbose=False, **kwargs):
    """CSV data loader.
    
        Parameters
        ---------
        data_source: csv file with data, separated by sep.
        chunk_size: the size of chunk to be used while reading the data, if used returned type 
                    is an iterator not a numpy array.
        sep: separator in the csv file, e.g. line "1,2,3\n" has separator comma, while "1 2 3\n" has space.
    
        Returns
        -------
        data: either numpy array with data or lazy iterator if chunk_size was provided.
    """
    data = pd.read_csv(data_source, sep=sep, chunksize=chunk_size, header=None, **kwargs)
    logger.debug("data type: {}".format(type(data)))
    logger.debug("CSV loaded, into iterator data.")
        
    if isinstance(data, pd.DataFrame):
        return data.values
    else:
        return data

def chunks(iterable, chunk_size=1):
    """Chunkls genertaor"""
    iterator = iter(iterable)
    for first in iterator:
        yield np.array(list(chain([first], islice(iterator, chunk_size - 1))))

def load_gz(data_source, chunk_size=None, verbose=False):
    """Gz data loader. Reads compressed file."""
    raise NotImplementedError
    
def load_tar(data_source, chunk_size=None, verbose=False):
    """Tar data loader. Reads compressed file."""
    raise NotImplementedError

class DataSourceIdentifier():
    """Class that recognizes the type of given file and provides with an
       adequate loader. It currently supports CSV files only.
     
       Properties
       ----------
       supported_types: dictionary of supported types along with their adequate loaders,
                        to support a new data type this dictionary need to be updated with
                        key as the file extension and value as the loading function name.
                        TODO: the supported types could be stored in a json file as a configuration.
    
       Example
       -------
       >>>identifier = DataSourceIdentifier("data.csv")
       >>>loader = identifier.fetch_loader()
       >>>X = loader("data.csv")
    """
    def __init__(self, data_source, verbose=False):
        """Initialise DataSourceIdentifier.
            
           Parameters
           ----------
           data_source: name of a file to be recognized.
        """
        self.verbose = verbose
        self.data_source = data_source
        self.supported_types = {"csv": load_csv, 
                                "txt": load_csv, 
                                "gz": load_csv, 
                                "tar": load_tar,
                                "iter": chunks
                               }
        self._identify()
                
    def fetch_loader(self):
        """Returns adequate loader required to read  identified file."""
        logger.debug("Return adequate loader that provides loading of data source.")
        return self.supported_types[self.src]
   
    def get_src(self):
        """Returns identified source type."""
        return self.src
 
    def _identify(self):
        """Identifies the data file type based on the file name."""
        if isinstance(self.data_source, str):
            self.src =  self.data_source.split(".")[-1] if "." in self.data_source else None           
            if self.src is not None and self.src not in self.supported_types:
                logger.debug("File type not supported! Supported types: {}".format(", ".join(self.supported_types)))
                self.src = None
        else:
            logger.debug("data_source is an object")
            if isinstance(self.data_source, Iterable):
                self.src = "iter"
                logger.debug("data_source is an iterable")
            else:
                logger.error("Object type not supported")

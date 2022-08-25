import chunk
from encodings import utf_8
import http
from logging import raiseExceptions
import sys
from http009 import http_response

import typing
import doctest

sys.setrecursionlimit(10000)


# NO ADDITIONAL IMPORTS!



# custom exception types for lab 6


class HTTPRuntimeError(Exception):
    pass


class HTTPFileNotFoundError(FileNotFoundError):
    pass


# functions for lab 6


def download_file(url, chunk_size=8192):
    """
    Yield the raw data from the given URL, in segments of at most chunk_size
    bytes (except when retrieving cached data as seen in section 2.2.1 of the
    writeup, in which cases longer segments can be yielded).

    If the request results in a redirect, yield bytes from the endpoint of the
    redirect.

    If the given URL represents a manifest, yield bytes from the parts
    represented therein, in the order they are specified.

    Raises an HTTPRuntimeError if the URL can't be reached, or in the case of a
    500 status code.  Raises an HTTPFileNotFoundError in the case of a 404
    status code.
    """
    if type(url) != str:
        raise ValueError('Please insert a string')
    if not url.startswith('http'):
        raise ValueError('URL Invalid')

    cached = {}

    # attempt to retreive the http_object
    try:
        http_object = http_response(url)
    except:
        raise HTTPRuntimeError
    
    # check status for errors and redirects
    response = http_object.status
    if response == 404:
        raise HTTPFileNotFoundError
    elif response == 500:
        raise HTTPRuntimeError
    # if redirect needed, call download file again and yield object
    elif response == 301 or response == 302 or response == 307:
        gen_object = download_file(http_object.getheader('location'), chunk_size)
        
        for elt in gen_object:
            yield elt
    else:
        # handle .parts
        if url.endswith('.parts') or http_object.getheader('content-type') == 'text/parts-manifest':
            # reads first line of code
            line = http_object.readline().decode('utf_8').strip()
            print(line)
          
            
            while line != '':
                # create a set to store the urls
                section = set()

                can_cache = False
                while line != '--' and line != '':
                    # add each url that is not empty or hyphen
                    section.add(line)
                    # read the next url
                    line = http_object.readline().decode('utf_8').strip()
                # read the next section
                line = http_object.readline().decode('utf_8').strip()
            
                # if url can be cached
                if '(*)' in section:
                    can_cache = True
                
                for part in section:
                    try:
                        if can_cache:
                            # try retreiving it or call download file and save it
                            generator = cached.get(part, '')
                            if generator == '':
                                generator = list(download_file(part))
                                address = line
                                cached[address] = generator
                        else:
                            # just download the file
                            generator = list(download_file(part))
                        # yield and break out of loop
                        for elt in generator:
                            yield elt
                        break
                    except:
                        pass
                
            
        else:
            # download file by chunk_size
            read_http = http_object.read(chunk_size)
            while read_http != b'':
                yield read_http
                read_http = http_object.read(chunk_size)
                        
               
def files_from_sequence(stream):
    """
    Given a generator from download_file that represents a file sequence, yield
    the files from the sequence in the order they are specified.
    """

   
    num_files = 0

    # goes through generator
    files = next(stream)

    # loop when file is not empty
    while files != b'':

        # if next(stream) does not have enough length, keep adding until 4
        while len(files) < 4:
            files += next(stream)

        # collect size of the files
        num_files = int.from_bytes(files[0:4], 'big')
        
        # remove unnecessary files
        files = files[4:]

        # while next(stream) not enough length for yielding all files, keep adding
        while len(files) < num_files:
            files += next(stream)
        
        # yield files
        yield files[0:num_files]
        
        # remove unnecessary files
        files = files[num_files:]
        

     

if __name__ == "__main__":
    
    # for i in download_file('https://py.mit.edu/spring22/info/basics'):
    #     pass

    generator = download_file("http://mit.edu/6.009/www/lab6_examples/yellowsub.txt.parts")
    print(list(generator))
    # r = http_response('https://py.mit.edu')
    # for url in  ('https://py.mit.edu', 'https://py.mit.edu/spring22/labs/lab11', 'https://py.mit.edu/spring22/info/basics','https://discourse6009.mit.edu/', 'http://nonexistent.mit.edu/some_file.jpg'):
    #     if http_response(url).status == 301 or http_response(url).status == 302 or http_response(url).status == 307:
    #         print(url)
    # print(len(http_response('https://py.mit.edu/spring22/info/basics').readline()))

    # open file, write in to it a append, b for bytes
    # open file iteratre through generator, 
    

     # r = http_response('https://py.mit.edu')
    # for url in  ('https://py.mit.edu', 'https://py.mit.edu/spring22/labs/lab11', 'https://py.mit.edu/spring22/info/basics','https://discourse6009.mit.edu/', 'http://nonexistent.mit.edu/some_file.jpg'):
    #     if http_response(url).status == 301 or http_response(url).status == 302 or http_response(url).status == 307:
    #         print(url)
    # print(len(http_response('https://py.mit.edu/spring22/info/basics').readline()))

    # open file, write in to it a append, b for bytes
    # open file iteratre through generator, 
    pass
    # lab_name = sys.argv[0]
    # url = sys.argv[1]
    # filename = sys.argv[2]

    
    # # file_contents = download_file(url)

    # # with open(filename, 'ab') as file:
    # #     for i in file_contents:
    # #         file.write(i)
        
    # file_contents = download_file(url)
    # sequence = files_from_sequence(file_contents)
    
    # cnt = 1

    # while True:
    #     with open('file'+str(cnt)+filename, 'ab') as file:
    #         file.write(next(sequence))
    #     cnt +=1
    

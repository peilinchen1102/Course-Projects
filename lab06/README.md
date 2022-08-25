# Multi-Part File Downloader

## Introduction
One way to handle the problem of reliably storing large files is to break them into pieces that are placed on multiple disks, or on multiple machines. This way, if something goes wrong with a particular file (and/or with a particular machine as a whole), the file is still available.

In this lab, you will build a multi-part downloader that assembles a data stream from multiple parts streaming individually from multiple machines. It allows the same part to be stored redundantly in multiple locations so it can be resilient to failures. Since the multipart streams you will be downloading may be nonterminating, your program will assemble the stream incrementally from its parts as they are downloaded, displaying the file or streamed sequence of files (an animated sequence of images, for example) as the download progresses.

This page describes the specification for the lab, but it also aims to provide some review on a few aspects of Python that were discussed in lecture but that have not been used explicitly in a lab yet.


2.1) Downloads
Throughout this lab, we will be interested in downloading files from various web servers. We have provided a function called http_response, which is defined in http009.py, to help you with this task. http_response is a thin wrapper around functionality from Python's built-in http.client module.

That function takes a single argument (a string representing the URL of a resource we wish to look up), and it returns an HTTPResponse object.

In particular, we are interested in three or four attributes/methods of these objects. If r is the result of calling http_response, then:
- r.status gives the HTTP status code that the server returned. For this lab, we will need to know that
301, 302, and 307 represent redirects.
404 means that the specified file was not found.
500 means that an error occurred on the server.
- r.getheader(name) returns the HTTP response header associated with the given name.
- r.getheader('location') will provide the location if we were redirected.
- r.getheader('content-type') will tell you the media type of the response of a successful request.
- r.read(num_bytes) returns a bytestring containing at most num_bytes number of bytes read from the body of the response. If no more bytes can be read, returns an empty bytestring b''. If num_bytes is not given, return the entire page contents. See section 10 if you are unfamiliar with Python bytestrings.
- r.readline() returns a bytestring containing the next line of the body of the response. It returns an empty bytestring b'' if no more bytes can be read.
to decode a bytestring into a string run b''.decode("utf-8")

## File Manifests
In addition to being able to download regular files, there are also file manifests, which is a way of specifying how a particular file is broken down into parts. File manifests in our implementation will either end with .parts or have the Content-Type header equal to 'text/parts-manifest'.

The manifest contains several parts, each adjacent pair of which is separated by a line containing exactly two hyphens --. For example, a file picture.jpg might be broken down into three parts, which could be specified with:
```
http://mymachine.mit.edu/picture.jpg-part1
--
http://mymachine.mit.edu/picture.jpg-part2
--
http://mymachine.mit.edu/picture.jpg-part3
```

To download the contents of this file specified by the manifest, you would need to download each of the individual parts and concatenate them together.

In addition, the manifest can provide alternatives for each section (so that if one URL doesn't work we can use the other one):
```
http://mymachine.mit.edu/picture.jpg-part1
http://yourmachine.mit.edu/picture.jpg-part1
--
http://mymachine.mit.edu/picture.jpg-part2
http://yourmachine.mit.edu/picture.jpg-part2
--
http://mymachine.mit.edu/picture.jpg-part3
http://yourmachine.mit.edu/picture.jpg-part3
```

## Caching
Manifest files may have parts that are replicated multiple times in the same file. This may be obvious from the previous manifest file, which is an endless stream of two replicated text parts. Thus, we will also add the capability to cache parts of files within a single download (though we will explicitly not cache these results across multiple downloads).

Caching is a bad idea if a file changes too frequently. Therefore we are not going to cache all the files we download. We will only cache for a part if (*) is listed as a possible URL for that part in the manifest file. This indicates that the manifest file deems a particular part to be largely fixed content, so it can be safely cached within a single download.

When downloading, if we reach a part that is marked as cacheable (contains (*)), we should first check to see if any of the URLs has been cached. If the file has already been cached, we should simply use that result (without making any HTTP requests). If not, we should send a HTTP request to download the first URL in the part and store the result in the cache. Importantly, caching should not interrupt the streaming (i.e., we should still be able to stream from files as we download them, rather than having to wait for the whole file to be downloaded first).

Parts in the manifest that are not marked with an (*) should never be cached. This requires that the content for these links should not be read from the cache or stored to the cache. Thus, a sample Manifest file that supports caching could look like the following:
```
(*)
http://mymachine.mit.edu/verse.txt
http://yourmachine.mit.edu/verse.txt
http://hermachine.mit.edu/verse.txt
--
http://yourmachine.mit.edu/chorus.txt
(*)
--
http://mymachine.mit.edu/endless.txt.parts
```
For simplicitly, it is not necessary to support caching manifest files themselves, and it is not necessary to support caching infinite files (i.e., you can assume that any file you are being asked to cache is finite in length).

## File Sequences
In addition to manifests, we would also like to handle file sequences. In general, a file sequence is a single stream of bits that represents a sequence of multiple files. We'll use a format of our own invention, but it's not too different from, for example, a movie file (which can be thought of as a sequence of frames, each of which is an image).

If a URL contains the string -seq, the resulting stream represents a sequence of files. Each sub-file in a sequence is represented as:

4 bytes containing the length of the file (in bytes, represented as a single big-endian unsigned integer (see subsection 10.4)), followed by
the raw bytes contained in the file (there should be as many bytes as were specified in the length field).
As an example, consider a file consisting of the following 5 bytes (shown in hexadecimal):
```
36 2E 30 30 35
```
We could encode a file sequence consisting of these two files with the following stream of 19 bytes (4-byte length + 5-byte file + 4-byte length + 6-byte file):
```
00 00 00 05 36 2E 30 30 35 00 00 00 06 72 75 6C 65 73 21
```
If a URL contains -seq and is also a manifest (the URL ends with .parts or the content type is text/parts-manifest), then it represents a manifest file that, when all parts are concatenated, represents a file sequence.
## Implementation
### Basic Downloads
We'll start by discussing basic downloads. You should fill in the body of the download_file function to implement a basic "streaming" downloader1.

download_file should be a generator that yields the result of the response as bytestrings of at most CHUNK_SIZE length (it should yield bytestrings of this size until it is no longer able to do so, at which point it should yield one bytestring of smaller size if the file contains additional content).

Note that, throughout this lab, we will assume that any URL refers to a potentially infinite stream (for example, a stream from a webcam). As such, your download_file function should not download the entire contents of the file and yield values from that result; rather, it should yield chunks of the file as they are downloaded.

We will also assume that any URL refers to arbitrary binary data (it could be an image, or text, or random bytes, etc.). Aside from checking whether the URL refers to a file manifest, your code should not need to change its behavior based on the type of the data (or the content-type header).

There are a couple of additional complications:

- If a request results in a redirect (status codes 301, 302, or 307 for our purposes), your downloader should follow that redirect and try the location to which you are being redirected.
- If a request gives a 404 status code, your downloader should raise a FileNotFoundError.
- If a request gives a 500 status code, or if the connection was not made because of a network error, your downloader should raise a RuntimeError.
- A status code of 200 indicates a successful request.

### Hadling Manifests
If the location given at initialization time ends with .parts or if the Content-Type header associated with a request is 'text/parts-manifest', then it represents a file manifest. In this case, rather than simply yielding the contents of that .parts file, download_file should instead yield the bytes from each of the files specified in the manifest, in the order they are specified.

In order to keep things as smooth as possible, your function should start streaming the first part as soon as it is available, rather than waiting for all parts to be available before streaming.

You should also make sure that your program properly caches files that were indicated with (*) in any file manifests that were given (so that, if we have already retrieved their contents once in the process of downloading the file, we do not do so a second time). Your program should not cache other files.

If a file is cached, it is OK to yield the entire contents of the cached file as one bytestring (rather than splitting it up into chunks and yielding those separately).

Importantly, the cache should not persist between calls to download_file. That is, starred files that we try to download multiple times within a single top-level call to download_file should be cached, but that cache should be invalidated with every new top-level call to download_file.

### Handling File Sequences
The description above should be enough for downloading file sequences, but it is not yet enough for interpreting them. You should not need to change any behavior in your downloader to account for file sequences. But the GUI needs to know something about how to handle file sequences in order to properly display them, so we'll add a small piece of functionality to allow us to grab individual files from the sequence.

Write a new generator called files_from_sequence(stream). Given a generator of the form described for download_file, files_from_sequence should yield the contents of each file contained in the sequence, in the order they are specified. Note that each of the chunks yielded from download_file might contain multiple files, or it might not contain an entire file. Your function will need to account for both of these cases.

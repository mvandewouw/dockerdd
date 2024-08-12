#!/usr/bin/env python3

import docker
import os
import sys
import yaml
import json

# Setup local docker client connection
dockerclient = docker.from_env()

def get_local_image_manifest_digest(image_reference: str):
    try:
        output = os.popen(f"docker manifest inspect -v {image_reference}").read()
        manifest_info = json.loads(output)

        digest = manifest_info['Descriptor']['digest']
        return digest
    except Exception as e:
        print(f"FAIL to get local image manifest digest: {e}")
        return None

# Import yaml file
if len(sys.argv) > 1:
    job_file = sys.argv[1]
else:
    job_file = 'jobs.yaml'

from yaml.loader import SafeLoader
with open(job_file, 'r') as f:
    dddata = yaml.load(f, Loader=SafeLoader)

# Process jobs
for job in dddata['jobs']:
    print(f"Job: {job}")

    # Process imagelists for given job
    for imagelist in dddata['jobs'][job]['imagelists']:
        source = dddata['jobs'][job]['source']
        target = dddata['jobs'][job]['target']
        source_addr = dddata['registries'][source]['address']
        target_addr = dddata['registries'][target]['address']

        if 'folder' in dddata['registries'][source]:
            target_folder = '/' + dddata['registries'][source]['folder'] + '/'
        else:
            target_folder = '/'

        print(f"- Sync imagelist {imagelist} from {source} to {target}")

        # Process images in given imagelist
        for image in dddata['imagelists'][imagelist]:
            image_name = image['name']
            lts = image.get('lts', False)
            result = 'ok'
            image_name, image_tag = image_name.split(':')
            if source_addr == 'default':
                source_full = image_name + ':' + image_tag
            else:
                source_full = source_addr + '/' + image_name + ':' + image_tag
            
            target_full = target_addr + target_folder + image_name + ':' + image_tag

            print(f"  - {image_name}:{image_tag}: ", end='', flush=True)

            # Check if image is already in target registry
            osout = os.system(f"docker manifest inspect {target_full} > /dev/null 2>&1")
            if osout == 0 and not lts:
                print("cached... ok")
            else:
                # Pull image from source registry
                print(f"pull... ", end='', flush=True)
                try:
                    dockerimage = dockerclient.images.pull(source_full)
                except Exception as e:
                    print(f"FAIL: {e}")
                    if 'dockerimage' in locals():
                        del dockerimage
                    continue
    
                # Tag new registry
                if 'dockerimage' in locals():
                    print("tag... ", end='', flush=True)
                    try:
                        dockerimage.tag(target_full)
                    except Exception as e:
                        print(f"FAIL: {e}")
                        dockerclient.images.remove(source_full)
                        if 'dockerimage' in locals():
                            del dockerimage
                        continue
                    # Get and write the local image digest to a file
                    digest = get_local_image_manifest_digest(target_full)
                    if digest:
                        with open(f"digest.txt", 'a') as file:
                            file.write(f"{target_full}@{digest}\n")
                        print(f" (Digest written {target_full} {digest} digest.txt)")
    
                # Push image to target registry
                if 'dockerimage' in locals():
                    print("push... ", end='', flush=True)
                    try:
                        pushed = dockerclient.images.push(repository=target_full)
                        # Cleanup target image (tag)
                        print("untag... ", end='', flush=True)
                        dockerclient.images.remove(target_full)
                    except Exception as e:
                        print(f"FAIL: {e}")
                        continue
    
                    # Check if image is available in target repo
                    print("verify:", end='', flush=True)
                    osout = os.system(f"docker manifest inspect {target_full} >/dev/null 2>/dev/null")
                    if osout != 0:
                        print("error... ", end='', flush=True)
                        result = 'FAIL'
                    else:
                        print("ok... ", end='', flush=True)

                    # Cleanup source image
                    print("cleanup... ", end='', flush=True)
                    try:
                        dockerclient.images.remove(source_full)
                    except:
                        pass
                    print(result)


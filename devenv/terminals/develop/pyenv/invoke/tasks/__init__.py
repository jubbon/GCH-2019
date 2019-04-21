#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from invoke import task

from .helpers import working_directory


DOCKER_REGISTRY = "docker.citylix.ru:5000"
IMAGE_DEFAULT_VERSION = "latest"

COMPONENTS = {}


@task
def all(ctx):
    '''
    Mark all components for execute next invoke tasks
    '''
    base(ctx)


@task
def base(ctx):
    '''
    Mark base component for execute next invoke tasks
    '''
    COMPONENTS['base'] = {"dir": ".", "image_name": "gch/base"}


@task
def geocoder(ctx):
    '''
    Mark geocoder component for execute next invoke tasks
    '''
    COMPONENTS['geocoder'] = {"dir": ".", "image_name": "gch/geocoder"}


@task
def gis(ctx):
    '''
    Mark gis component for execute next invoke tasks
    '''
    COMPONENTS['gis'] = {"dir": ".", "image_name": "gch/gis"}

@task
def build(ctx):
    '''
    Build Docker-image
    '''
    if not COMPONENTS:
        all(ctx)

    for _, component in COMPONENTS.items():
        image = "{}:{}".format(component["image_name"], IMAGE_DEFAULT_VERSION)
        with working_directory(component["dir"]):
            print("Building image {}".format(image))
            ctx.run("docker build -t {} .".format(image))


@task
def release(ctx, version=None):
    '''
    Push Docker-image to private registry
    '''
    version = os.getenv("VERSION",
                        IMAGE_DEFAULT_VERSION) if version is None else version

    if not COMPONENTS:
        all(ctx)

    for _, component in COMPONENTS.items():
        image = "{}:{}".format(component["image_name"], IMAGE_DEFAULT_VERSION)
        repo_image = "{}/{}:{}".format(DOCKER_REGISTRY,
                                       component["image_name"], version)
        with working_directory(component["dir"]):
            print("Releasing image {}".format(image))
            ctx.run("docker tag {} {}".format(image, repo_image))
            ctx.run("docker push {}".format(repo_image))

    # if version != "latest":
    #     ctx.run("git tag backend-rabbitmq-{}".format(version))
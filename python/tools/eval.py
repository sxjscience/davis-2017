#!/usr/bin/env python

# ----------------------------------------------------------------------------
# A Benchmark Dataset and Evaluation Methodology for Video Object Segmentation
#-----------------------------------------------------------------------------
# Copyright (c) 2016 Federico Perazzi
# Licensed under the BSD License [see LICENSE for details]
# Written by Federico Perazzi
# ----------------------------------------------------------------------------

"""
Evaluate a technique and (optionally) store results in YAML file.
"""

import os.path as osp
import argparse
import itertools

import h5py
import yaml
import davis
import numpy as np

from davis import cfg
from davis.misc import Timer, log
from davis.dataset import db_eval

from prettytable import PrettyTable

def parse_args():
  """
  Parse input arguments.
  """

  parser = argparse.ArgumentParser(
    description="""Evaluate a technique, print and/or store results.""")

  parser.add_argument(
      '-i','--input',required=True,type=str,
      help='Path to the technique to be evaluated')

  parser.add_argument(
      '-o','--output',default=None,type=str,
      help='Output folder')

  parser.add_argument(
      '--metrics',default=['J','F'],nargs='+',type=str,choices=['J','F','T'])

  parser.add_argument(
      '--year','-y',default=cfg.YEAR,type=str,choices=['2016','2017'])

  parser.add_argument(
      '--phase','-p',default=cfg.PHASE.name,type=str,choices=[e.name.lower()
        for e in davis.phase])

  parser.add_argument('--single-object',action='store_true')

  args = parser.parse_args()

  # Cast string to Enum
  args.phase = davis.phase[args.phase.upper()]

  return args


if __name__ == '__main__':

  args = parse_args()

  log.info('Loading DAVIS year: {} phase: {}'.format(
    args.year,args.phase))

  # Load DAVIS
  db = davis.dataset.DAVISLoader(args.year,
      args.phase,args.single_object)

  log.info('Loading video segmentations from: {}'.format(args.input))

  # Load segmentations
  segmentations = [davis.dataset.Segmentation(
    osp.join(args.input,s),args.single_object) for s in db.iternames()]

  # Evaluate results
  evaluation = db_eval(db,segmentations,args.metrics)

  # Print results
  table = PrettyTable(['Method']+[p[0]+'_'+p[1] for p in
    itertools.product(args.metrics,davis.cfg.EVAL.STATISTICS)])

  table.add_row([osp.basename(args.input)]+["%.3f"%np.round(
    evaluation['dataset'][metric][statistic],3) for metric,statistic
    in itertools.product(args.metrics,davis.cfg.EVAL.STATISTICS)])

  print str(table) + "\n"

  # Save results
  if args.output is not None:
    log.info("Saving output in: {}".format(args.output))
    with open(args.output,'w') as f:
      yaml.dump(evaluation,f)


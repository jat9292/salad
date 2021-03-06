import sys
import os
import os.path as osp
sys.path.append(osp.dirname(__file__))

import torch
from torch import nn

from salad import solver, datasets
from salad.utils import config 

import salad.models.digits.corr as models

if __name__ == '__main__':

    parser = config.DomainAdaptConfig('CORAL')
    args   = parser.parse_args()

    # Network
    if osp.exists(args.checkpoint):
        print("Resume from checkpoint file at {}".format(args.checkpoint))
        model = torch.load(args.checkpoint)
    else:
        model = models.SVHNmodel()

    # Dataset
    data = datasets.da.load_dataset2(path="data", train=True)

    train_loader = torch.utils.data.DataLoader(
        data[args.source], batch_size=args.sourcebatch,
        shuffle=True, num_workers=args.njobs)
    val_loader   = torch.utils.data.DataLoader(
        data[args.target], batch_size=args.targetbatch,
        shuffle=True, num_workers=args.njobs)

    dataset = datasets.JointLoader(train_loader, val_loader)

    # Initialize the solver for this experiment
    experiment = solver.da.DeepCoralSolver(model, dataset,
                               n_epochs=args.epochs,
                               savedir=args.log,
                               dryrun = args.dryrun,
                               learningrate = args.learningrate,
                               gpu=args.gpu if not args.cpu else None)

    experiment.optimize()
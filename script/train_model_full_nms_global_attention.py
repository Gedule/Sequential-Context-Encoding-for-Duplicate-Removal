import sys
import os.path as osp
sys.path.append(osp.abspath(osp.join(__file__, '../../')))
from models.rnn_model_full_global_attention import Encoder_Decoder
from dataset.multi_dataset_full_nms import TrainDataset, unique_collate
from solver.solver_full_nms_weight import solver, load_checkpoint
import torch
import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser(description='Train RNN NMS')
    parser.add_argument('--hidden_size', 
                        default=128,
                        type=int,
                        help='the hidden size of RNN')

    parser.add_argument('--base_path', 
                        default='/data/luqi/dataset/pytorch_data/',
                        help='the data path of RNN')

    parser.add_argument('--img_list',
                        default='train.txt',
                        help='the img_list')

    parser.add_argument('--use_mode',
                        default='unique',
                        help='the method of score_box_fusion')

    parser.add_argument('--output_dir',
                        default='/data/luqi/RNN_NMS/test1/',
                        help='the save path of output_dir')

    parser.add_argument('--num_epochs',
                        default=7,
                        type=int,
                        help='the number of training epoch')

    parser.add_argument('--learning_rate',
                        default=0.01,
                        type=float,
                        help='learning_rate of model')

    parser.add_argument('--step',
                        default=5,
                        type=int,
                        help='stepsize of model')

    parser.add_argument('--load',
                        default=0,
                        type=int,
                        help='load')

    parser.add_argument('--weight',
                        default=2,
                        type=float,
                        help='weight')

    parser.add_argument('--attn_type',
                        default='dot',
                        help='the attn_type')
    
    args = parser.parse_args()
    return args



if __name__ == '__main__':
    args = parse_args()
    # initialization
    model_dir = os.path.join(args.output_dir, 'model/')
    log_info_dir = os.path.join(args.output_dir, 'log/')
    load_pth = os.path.join(model_dir, 'latest.pth')

    if not osp.exists(model_dir):
        os.makedirs(model_dir)

    if not osp.exists(log_info_dir):
        os.makedirs(log_info_dir)

    output_dir = [model_dir, log_info_dir]

    use_cuda = torch.cuda.is_available()

    cls_list = ['_' for _ in range(81)]
    # dataset
    train = TrainDataset(args.base_path, args.img_list, args.use_mode, cls_list, weight=args.weight)
    train_loader = torch.utils.data.DataLoader(train, batch_size=1, num_workers=1, collate_fn=unique_collate, pin_memory=False, shuffle=True)

    # model
    model = Encoder_Decoder(args.hidden_size, attn_type=args.attn_type)
    if args.load:
        continue_epochs, continue_iters = load_checkpoint(model, load_pth)

    if use_cuda:
        model = model.cuda()

    if not args.load:
        solver(model, train_loader, args.num_epochs, print_every=20, save_every=10000, output_dir=output_dir, learning_rate=args.learning_rate, step=args.step)
    else:
        solver(model, train_loader, args.num_epochs, print_every=20, save_every=10000, output_dir=output_dir, learning_rate=args.learning_rate, step=args.step, continue_epochs=continue_epochs, continue_iters=continue_iters)


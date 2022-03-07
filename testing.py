import sys
sys.path.insert(0,'modules/targetAcquisition/Yolov5_DeepSort_Pytorch')
sys.path.append('modules/targetAcquisition/Yolov5_DeepSort_Pytorch/deep_sort/deep/reid')
import multiprocessing as mp
from modules.targetAcquisition.testWorker import targetAcquisitionWorker, imageFaker

def run(): 
    pipelineIn = mp.Queue()
    pause = mp.Lock()
    quit = mp.Queue()

    processes = [
        mp.Process(target = targetAcquisitionWorker, args = (pause, quit, pipelineIn)),
        mp.Process(target = imageFaker, args = (pause, quit, pipelineIn)),
    ]

    for p in processes:
        print("starting proccess")
        p.start()
        
    for p in processes:
        p.join()

if __name__ == '__main__':
    run()
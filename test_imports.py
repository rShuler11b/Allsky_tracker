try:
    import numpy
    import cv2
    import tqdm
    import easydict
    import multiprocess
    import onnxruntime
    from MetDetPy import MeteorDetection

    print("All libraries imported successfully!")
except ImportError as e:
    print(f"Error importing library: {e}")

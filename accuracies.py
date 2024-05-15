from Devinci.analysis.ROC import _Confusion_Matrix_Dual as conf
from Devinci.analysis.ROC import ChannelBound, Colour_Tag, Camera, camera_model

ch1 = ChannelBound(lower_bound=0,
                   upper_bound=55,
                   channel="HSV-Saturation",
                   True_Pos=0,
                   False_Pos=0,
                   pres=0,
                   )

ch2 = ChannelBound(lower_bound=1,
                   upper_bound=141,
                   channel="YCbCr-Chroma Blue",
                   True_Pos=0,
                   False_Pos=0,
                   pres=0,
                   )

TPR, FPR, Precision, Accuracy = conf(Camera(camera_model.OV5640),
     CH1 = ch1,
     CH2 = ch2
    )

print(TPR, FPR, Precision, Accuracy)


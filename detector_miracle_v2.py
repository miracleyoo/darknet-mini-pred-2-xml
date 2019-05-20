# Stupid python path shit.
# Instead just add darknet.py to somewhere in your python path
# OK actually that might not be a great idea, idk, work in progress
# Use at your own risk. or don't, i don't care

import sys, os

import darknet as dn
import argparse
import pdb
from PIL import Image
from lxml.etree import Element, SubElement, tostring
import pprint
from xml.dom.minidom import parseString

dn.set_gpu(0)


class XMLRes(object):
    def __init__(self, folder_name, file_name, img_size):
        self.node_root = Element('annotation')
        self.node_folder = SubElement(self.node_root, 'folder')
        self.node_folder.text = folder_name
        self.node_filename = SubElement(self.node_root, 'filename')
        self.node_filename.text = file_name
        self.node_owner = SubElement(self.node_root, 'owner')
        self.node_name = SubElement(self.node_owner, 'name')
        self.node_name.text = "MiracleYoo_Dian"
        self.node_size = SubElement(self.node_root, 'size')
        self.node_width = SubElement(self.node_size, 'width')
        self.node_width.text = str(img_size[0])
        self.node_height = SubElement(self.node_size, 'height')
        self.node_height.text = str(img_size[1])
        self.node_depth = SubElement(self.node_size, 'depth')
        self.node_depth.text = '3'

    def add_obj(self, name, difficult, box):
        self.node_object = SubElement(self.node_root, 'object')
        self.node_name = SubElement(self.node_object, 'name')
        self.node_name.text = name.decode()
        self.node_difficult = SubElement(self.node_object, 'difficult')
        self.node_difficult.text = str(difficult)
        self.node_bndbox = SubElement(self.node_object, 'bndbox')
        self.node_xmin = SubElement(self.node_bndbox, 'xmin')
        self.node_xmin.text = str(round(box[0]))
        self.node_ymin = SubElement(self.node_bndbox, 'ymin')
        self.node_ymin.text = str(round(box[1]))
        self.node_xmax = SubElement(self.node_bndbox, 'xmax')
        self.node_xmax.text = str(round(box[2]))
        self.node_ymax = SubElement(self.node_bndbox, 'ymax')
        self.node_ymax.text = str(round(box[3]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="==> Start prediction!")
    parser.add_argument("path", type=str ,help="the path of the directory.")
    args = parser.parse_args()
    dirs = [os.path.join(args.path, adir) for adir in os.listdir(args.path) if not adir.startswith('.')]
    dirs_xml = [os.path.join("xml_res", adir) for adir in os.listdir(args.path) if not adir.startswith('.')]
    if not os.path.exists("xml_res"): os.mkdir("xml_res")
    # # Use COCO Datasets
    # net = dn.load_net(b"cfg/yolov3.cfg", b"yolov3.weights", 0)
    # meta = dn.load_meta(b"cfg/coco.data")

    net = dn.load_net(b"cfg/yolov2-voc.cfg", b"yolo-voc.weights", 0)
    meta = dn.load_meta(b"cfg/voc.data")

    for adir, adir_xml in zip(dirs, dirs_xml):
        print("==> Now processing dir:", adir)
        if not os.path.exists(adir_xml): os.mkdir(adir_xml)
        files = [os.path.join(adir, afile) for afile in os.listdir(adir) if not afile.startswith('.') and afile.endswith('.jpg')]
        for afile in files:
            print("==> Now processing file:", afile)
            xml_name = os.path.join(adir_xml ,os.path.splitext(os.path.split(afile)[1])[0] + '.xml')
            img=Image.open(afile)
            xml_res = XMLRes(adir, afile, img.size)
            res = dn.detect(net, meta, afile.encode())
            # print(res)
            for obj in res:
                xml_res.add_obj(*obj)
                # pprint(xml)
            xml = tostring(xml_res.node_root, pretty_print=True).decode()  #格式化显示，该换行的换行
            with open(xml_name, 'w+') as f:
                f.write(xml)
            # dom = parseString(xml)
            # print(xml)

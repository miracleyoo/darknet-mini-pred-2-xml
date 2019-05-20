import sys, os
from PIL import Image
import darknet as dn
import argparse
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

def add_obj(root, name, difficult, box):
    node_object = Element('object')
    node_name = Element('name')
    node_name.text = name.decode()
    node_object.append(node_name)
    node_difficult = Element('difficult')
    node_difficult.text = str(difficult)
    node_object.append(node_difficult)
    node_bndbox = Element('bndbox')
    node_xmin = Element('xmin')
    node_xmin.text = str(round(box[0]))
    node_bndbox.append(node_xmin)
    node_ymin = Element('ymin')
    node_ymin.text = str(round(box[1]))
    node_bndbox.append(node_ymin)
    node_xmax = Element('xmax')
    node_xmax.text = str(round(box[2]))
    node_bndbox.append(node_xmax)
    node_ymax = Element('ymax')
    node_ymax.text = str(round(box[3]))
    node_bndbox.append(node_ymax)
    node_object.append(node_bndbox)
    root.append(node_object)

def prettyXml(element, indent, newline, level = 0): # elemnt为传进来的Elment类，参数indent用于缩进，newline用于换行  
    if element:  # 判断element是否有子元素  
        if element.text == None or element.text.isspace(): # 如果element的text没有内容  
            element.text = newline + indent * (level + 1)    
        else:  
            element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)  
    #else:  # 此处两行如果把注释去掉，Element的text也会另起一行  
        #element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level  
    temp = list(element) # 将elemnt转成list  
    for subelement in temp:  
        if temp.index(subelement) < (len(temp) - 1): # 如果不是list的最后一个元素，说明下一个行是同级别元素的起始，缩进应一致  
            subelement.tail = newline + indent * (level + 1)  
        else:  # 如果是list的最后一个元素， 说明下一行是母元素的结束，缩进应该少一个  
            subelement.tail = newline + indent * level  
        prettyXml(subelement, indent, newline, level = level + 1) # 对子元素进行递归操作  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="==> Start prediction!")
    parser.add_argument("path", type=str ,help="the path of the directory.")
    args = parser.parse_args()
    dirs = [os.path.join(args.path, adir) for adir in os.listdir(args.path) if not adir.startswith('.')]
    dirs_xml = [os.path.join("xml_res", adir) for adir in os.listdir(args.path) if not adir.startswith('.')]
    if not os.path.exists("xml_res"): os.mkdir("xml_res")

    net = dn.load_net(b"cfg/yolov2-voc.cfg", b"yolo-voc.weights", 0)
    meta = dn.load_meta(b"cfg/voc.data")

    for adir, adir_xml in zip(dirs, dirs_xml):
        print("==> Now processing dir:", adir)
        if not os.path.exists(adir_xml): os.mkdir(adir_xml)
        files = [os.path.join(adir, afile) for afile in os.listdir(adir) if not afile.startswith('.') and afile.endswith('.jpg')]
        xmls  = [os.path.join(adir, afile) for afile in os.listdir(adir) if not afile.startswith('.') and afile.endswith('.xml')]
        for afile, axml in zip(files, xmls):
            print("==> Now processing file:", afile)
            xml_name = os.path.join(adir_xml ,os.path.splitext(os.path.split(afile)[1])[0] + '.xml')
            img=Image.open(afile)
            root = ElementTree.parse(axml).getroot()

            res = dn.detect(net, meta, afile.encode())
            # print(res)
            for obj in res:
                add_obj(root, *obj)

            prettyXml(root, '\t', '\n')
            # root.write(xml_name, pretty_print=True)
            with open(xml_name, 'w+') as f:
                f.write((ElementTree.tostring(root,encoding="utf8",method="xml")).decode())


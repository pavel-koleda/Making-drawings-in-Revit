#! /usr/bin/env python
# -*- coding: utf-8 -*-
############_____________Name___________################
ScriptName = "ENECA-КР-Сбор информации-D1.0-v1.0"
############_____________Import___________################
import re
import clr

clr.AddReference("System")
from System.Collections.Generic import List

clr.AddReference("RevitAPI")
from Autodesk.Revit import DB

clr.AddReference("RevitAPIUI")
from Autodesk.Revit.UI import TaskDialog

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

########____________Defaults__________##########

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIDocument
app = uiapp.Application

################____________Transaction_______################
def get_parameter_value(parameter):
    if isinstance(parameter, DB.Parameter):
        storage_type = parameter.StorageType
        if storage_type == DB.StorageType.Integer:
            return parameter.AsInteger()
        elif storage_type == DB.StorageType.Double:
            return DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), parameter.DisplayUnitType)
        elif storage_type == DB.StorageType.String:
            return parameter.AsString()
        elif storage_type == DB.StorageType.ElementId:
            return parameter.AsElementId()
	

#scale = float(IN[1]) / 304.8
user_input_bool_value = IN[0]


#Находим все экземпляры аннотации на виде

annotations_on_view = DB.FilteredElementCollector(doc).OwnedByView(
    doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_MultiCategoryTags).WhereElementIsNotElementType().ToElements()

# Define the path where the CSV file will be saved
csv_path = r'C:\Users\User\Desktop\revit_data2.csv'

# Create a list to store data
data = [['Координата марки X ', 'Координата марки Y', 'Координата элемента X', 'Координата элемента Y',
         'Направление элемента X', 'Направление элемента Y', 'Ориентация марки', 'Длина элемента', 'Тип элемента'],]


X_coord_list = [tag.TagHeadPosition.X for tag in annotations_on_view]
Y_coord_list = [tag.TagHeadPosition.Y for tag in annotations_on_view]
X_center = (max(X_coord_list) - min(X_coord_list)) / 2
Y_center = (max(Y_coord_list) - min(Y_coord_list)) / 2
rr = []
tag_orientation_dict = {'Horizontal': 0, 'Vertical': 1}

# Loop through each wall and get its parameters
for tag in annotations_on_view:  
    tag_X_coord = tag.TagHeadPosition.X - X_center
    tag_Y_coord = tag.TagHeadPosition.Y - Y_center
    element = tag.GetTaggedLocalElement()
    element_center = element.GetTransform().Origin
    element_X_coord = element_center.X - X_center
    element_Y_coord = element_center.Y - Y_center
    element_X_direction = round(element.HandOrientation.X, 3)
    element_Y_direction = round(element.HandOrientation.Y, 3)
    tag_orientation = tag_orientation_dict[str(tag.TagOrientation)]
    element_length = element.Location.Curve.Length
    if re.match(r'^(П[а-яА-Я]+|П[а-яА-Я]+-|П|П-)\d+', tag.TagText):
        element_type = 'Прогон'
    elif re.match(r'^(Б[а-яА-Я]+|Б[а-яА-Я]+-|Б|Б-)\d+', tag.TagText):
        element_type = 'Балка'
    elif re.match(r'^(Ф[а-яА-Я]+|Ф[а-яА-Я]+-|Ф|Ф-)\d+', tag.TagText):
        element_type = 'Ферма'
    elif re.match(r'^(С[а-яА-Я]+|С[а-яА-Я]+-|С|С-)\d+', tag.TagText):
        element_type = 'Связь'
    elif re.match(r'^(Т[а-яА-Я]+|Т[а-яА-Я]+-|Т|Т-)\d+', tag.TagText):
        element_type = 'Тяж'
    elif re.match(r'^(У[а-яА-Я]+|У[а-яА-Я]+-|У|У-)\d+', tag.TagText):
        element_type = 'Раскрепление уголком'
    else:
        element_type = 'Неопределен'

    #length = get_parameter_value(tag.Parameter[DB.BuiltInParameter.ELEM_PARTITION_PARAM])
    data.append([str(tag_X_coord).replace(',', '.'), str(tag_Y_coord).replace(',', '.'), str(element_X_coord).replace(',', '.'), 
                 str(element_Y_coord).replace(',', '.'), str(element_X_direction).replace(',', '.'), 
                 str(element_Y_direction).replace(',', '.'), tag_orientation, str(element_length).replace(',', '.'), element_type])

c = DB.Point.Create(DB.XYZ(91.8635170603673, 29.2852597685434, 18.6738379381026))
# Show a message box to confirm that the file was save
message = 'CSV file saved to: {}'.format(csv_path)
TaskDialog.Show('Success', message)

OUT = data
'''
#Находим нужный экземпляр типоразмера аннотации
annotationsCollector = DB.FilteredElementCollector(doc)
genericAnnotations = annotationsCollector.OfClass(DB.FamilySymbol).OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsElementType().ToElements()

#Создаем два словаря с элементами и типами аннотаций
trays_dict = dict()
annotationFamilyTypes = dict()

#Заполняем словари. Также меняем тип аннотации, если ручной ввод
for ft in genericAnnotations:
	if "Аннотация_Прокладка_провода" in ft.Family.Name:
		trays_dict[str(DB.Element.Name.__get__(ft))] = []
		annotationFamilyTypes[str(DB.Element.Name.__get__(ft))] = ft
			
if user_input_bool_value:
	current_familyType = annotationFamilyTypes[user_genericAnnotation_type.Name]

#Составляем список Id выделенных элементов
selcted_elements_ids = uidoc.Selection.GetElementIds()
#Генерируем список элементов по их Id
selcted_elements = [doc.GetElement(id) for id in selcted_elements_ids]

#Проверка на горизонтальность элемента
def horizontal_check(element):
	element_start_offset_param = element.Parameter[DB.BuiltInParameter.RBS_START_OFFSET_PARAM]
	element_end_offset_param = element.Parameter[DB.BuiltInParameter.RBS_END_OFFSET_PARAM]
	if round(element_start_offset_param.AsDouble(), 5) == round(element_end_offset_param.AsDouble(), 5):
		return True

#Заполняем списки элементов для расставления аннотаций по условиям
for element in selcted_elements:
	if element.Category.Name == "Кабельные лотки" and "короб" not in element.Name.lower() and "канал" not in element.Name.lower():
		if horizontal_check(element):
			trays_dict["В_Лотке"].append(element)
	if ("короб" in element.Name.lower() or "канал" in element.Name.lower()) and (element.Category.Name == "Кабельные лотки" or element.Category.Name == "Короба"):
		if horizontal_check(element):
			trays_dict["В_Коробе"].append(element)
	if (element.Category.Name == "Короба" and "короб" not in element.Name.lower() and "металлорукав" 
        not in element.Name.lower() and "кабель" not in element.Name.lower() and "плинтус" not in element.Name.lower() and "канал" not in element.Name.lower()):
		if horizontal_check(element):
			trays_dict["В_Трубе"].append(element)
	if element.Category.Name == "Короба" and "металлорукав" in element.Name.lower():
		if horizontal_check(element):
			trays_dict["Металлорукав"].append(element)
	if element.Category.Name == "Короба" and "кабель" in element.Name.lower():
		if horizontal_check(element):
			trays_dict["Открытая_Прокладка"].append(element)
	if "плинтус" in element.Name.lower() and (element.Category.Name == "Кабельные лотки" or element.Category.Name == "Короба"):
		if horizontal_check(element):
			trays_dict["Под_Плинтусом"].append(element)

def create_annotations(horizontal_metal_conduits, familyType, annotation_step, familyTypeScale):
	#Создаем два списка металлорукавов с длиной меньше 2000мм и больше
	horizontal_metal_conduits_from1000to2000 = []
	horizontal_metal_conduits_more2000 = []
	scale_param = familyType.LookupParameter('Масштаб').AsDouble()
	newfamilyType = familyType
	newfamilyType.LookupParameter('Масштаб').Set(familyTypeScale)

	for metal_conduits in horizontal_metal_conduits:
		conduit_length_param = metal_conduits.Parameter[DB.BuiltInParameter.CURVE_ELEM_LENGTH]
		if get_parameter_value(conduit_length_param) >= 2000:
			horizontal_metal_conduits_more2000.append(metal_conduits)
		if 1000 <= get_parameter_value(conduit_length_param) < 2000:
			horizontal_metal_conduits_from1000to2000.append(metal_conduits)
			
	for conduit in horizontal_metal_conduits_from1000to2000:
		startPoint_1 = conduit.Location.Curve.GetEndPoint(0)
		endPoint_1 = conduit.Location.Curve.GetEndPoint(1)
		middlePoint_1 = (startPoint_1 + endPoint_1)/2
		#Создание аннотации
		familyInstance_1 = doc.Create.NewFamilyInstance(middlePoint_1, newfamilyType, doc.ActiveView)
		familyInstance_1.LookupParameter('Id - Owner').Set(str(conduit.Id.IntegerValue))
		cord_y_start_1 = startPoint_1.Y
		cord_y_end_1 = endPoint_1.Y
		vector_1 = endPoint_1 - startPoint_1
		#Условие необходимое, чтобы получить отрицательный угол в радианах, для повернутых больше 180 градусов элементов
		if cord_y_end_1 - cord_y_start_1 >= 0:
			current_vector_1 = vector_1.AngleTo(DB.XYZ.BasisX)
		else:
			current_vector_1 = -vector_1.AngleTo(DB.XYZ.BasisX)
		#Поворот аннотации
		DB.ElementTransformUtils.RotateElement(doc, familyInstance_1.Id, DB.Line.CreateUnbound(middlePoint_1, DB.XYZ.BasisZ), current_vector_1)

	for conduit in horizontal_metal_conduits_more2000:
		startPoint_2 = conduit.Location.Curve.GetEndPoint(0)
		endPoint_2 = conduit.Location.Curve.GetEndPoint(1)
		conduit_length_param_2 = conduit.Parameter[DB.BuiltInParameter.CURVE_ELEM_LENGTH]
		conduit_length_2 = get_parameter_value(conduit_length_param_2)
		number_of_points_2 = conduit_length_2 // annotation_step
		if conduit_length_2 - number_of_points_2 * annotation_step >= 600:
			current_number_of_points_2 = number_of_points_2 + 1
		else:
			current_number_of_points_2 = number_of_points_2

		vector_2 = endPoint_2 - startPoint_2
		for i in range(int(current_number_of_points_2) - 1):
			cord_x_start_2 = startPoint_2.X
			cord_y_start_2 = startPoint_2.Y
			cord_z_start_2 = startPoint_2.Z
			cord_x_end_2 = endPoint_2.X
			cord_y_end_2 = endPoint_2.Y
			#Определение координат каждой аннотации на линии
			first_cord_x = cord_x_start_2 + (cord_x_end_2 - cord_x_start_2) * (1 - annotation_step * current_number_of_points_2 / conduit_length_2) * 0.5
			first_cord_y = cord_y_start_2 + (cord_y_end_2 - cord_y_start_2) * (1 - annotation_step * current_number_of_points_2 / conduit_length_2) * 0.5
			cord_x_current = (cord_x_end_2 - cord_x_start_2) * (((i + 1.0) * annotation_step)/conduit_length_2) + first_cord_x
			cord_y_current = (cord_y_end_2 - cord_y_start_2) * (((i + 1.0) * annotation_step)/conduit_length_2) + first_cord_y
			current_Point_2 = DB.XYZ(cord_x_current, cord_y_current, cord_z_start_2)
			#Создание аннотации
			familyInstance_2 = doc.Create.NewFamilyInstance(current_Point_2, newfamilyType, doc.ActiveView)
			familyInstance_2.LookupParameter('Id - Owner').Set(str(conduit.Id.IntegerValue))

			if cord_y_end_2 - cord_y_start_2 >= 0:
				current_vector_2 = vector_2.AngleTo(DB.XYZ.BasisX)
			else:
				current_vector_2 = -vector_2.AngleTo(DB.XYZ.BasisX)
			DB.ElementTransformUtils.RotateElement(doc, familyInstance_2.Id, DB.Line.CreateUnbound(current_Point_2, DB.XYZ.BasisZ), current_vector_2)

#Составляем список элементов на которых нужно удалить аннотации
selcted_elements_ids_to_str = [str(id) for id in selcted_elements_ids]

TransactionManager.Instance.EnsureInTransaction(doc)

#Удаляем находящиеся экземпляры типоразмеров аннотации на виде
annotationsCollectorToDelete = DB.FilteredElementCollector(doc)
genericAnnotationsOnView = annotationsCollectorToDelete.OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).OwnedByView(
    doc.ActiveView.Id).WhereElementIsNotElementType().ToElements()
genericAnnotationsToDelete = []
for annot in genericAnnotationsOnView:
    try:
        if annot.LookupParameter('Id - Owner').AsString() in selcted_elements_ids_to_str or not doc.GetElement(DB.ElementId(int(annot.LookupParameter('Id - Owner').AsString()))):
            genericAnnotationsToDelete.append(annot)
    except:
        pass
for annotation in genericAnnotationsToDelete:
    annotation_name_param = annotation.Parameter[DB.BuiltInParameter.ELEM_FAMILY_PARAM]
    try:
        if annotation.Name in trays_dict.keys() and "Аннотация_Прокладка_провода" in annotation_name_param.AsValueString():
            doc.Delete(annotation.Id)
    except:
        pass
    	
#Расствноыка аннотаций аннотации на виде
for key in trays_dict.keys():
	if len(trays_dict[key]) > 0:
		if user_input_bool_value:
			create_annotations(trays_dict[key], current_familyType, annotation_step, scale)
		else:
			create_annotations(trays_dict[key], annotationFamilyTypes[key], annotation_step, scale)

TransactionManager.Instance.TransactionTaskDone()'''
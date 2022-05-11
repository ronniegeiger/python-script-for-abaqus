
from abaqus import *
from abaqusConstants import *
from caeModules import *
import regionToolset
import math
import random

# input attribute

# create base
myModel = mdb.models["Model-1"]
mysketch_1 = myModel.ConstrainedSketch(name='mysketch_1', sheetSize=200.0)
mysketch_1.rectangle(point1=(0.0, 0.0), point2=(100.0, 100.0))
myPart = myModel.Part(name='Part-Base', dimensionality=THREE_D, type=DEFORMABLE_BODY)
myPart.BaseSolidExtrude(sketch=mysketch_1, depth=100.0)
del mysketch_1

# assembly base
myAssembly = myModel.rootAssembly
myAssembly.Instance(name='Part-Base', part = myModel.parts["Part-Base"], dependent=ON)

def interCheck(point,center,radius1,radius2):
    sign = True
    for p in center:
        if sqrt((point[0]-p[0])**2+(point[1]-p[1])**2+(point[2]-p[2])**2) <= (radius1+radius2):
            sign = False
            break
    return sign

# material
## UHDC
mdb.models['Model-1'].Material(name='UHDC')
mdb.models['Model-1'].materials['UHDC'].ConcreteDamagedPlasticity(table=((30.0, 0.1, 1.16, 0.667, 0.0005), ))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteCompressionHardening(
    table=((1.35, 0.0), (45.12280675, 0.002628785), (47.3353288, 0.00304684), (
    48.91570169, 0.003488307), (49.86392542, 0.003953188), (50.18, 
    0.004441481), (48.89605839, 0.004989035), (47.61211679, 0.005536588), (
    34.77270073, 0.011012122), (27.06905109, 0.014297443), (15.0, 0.019444444), 
    (15.0, 0.029444444)))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteTensionStiffening(
    table=((2.5, 0.0), (5.05, 0.039812963), (4.915, 0.041817963), (4.78,
    0.043822963), (1.0, 0.099962963)))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteCompressionDamage(
    table=((0.0, 0.0), (0.37657826, 0.002628785), (0.395647673, 0.00304684), (
    0.415338728, 0.003488307), (0.435716498, 0.003953188), (0.456858269, 
    0.004441481), (0.483939538, 0.004989035), (0.508509155, 0.005536588), (
    0.676417688, 0.011012122), (0.7440183, 0.014297443), (0.833333333, 
    0.019444444), (0.863917237, 0.029444444)))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteTensionDamage(
    table=((0.0, 0.0), (0.931619258, 0.039812963), (0.934165243, 0.041817963),
    (0.936568391, 0.043822963), (0.980754991, 0.099962963)))
mdb.models['Model-1'].materials['UHDC'].Elastic(table=((27000.0, 0.2), ))
mdb.models['Model-1'].HomogeneousSolidSection(name='UHDC', material='UHDC', thickness=None)
p = mdb.models['Model-1'].parts['Part-Base']
c = p.cells
cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(cells=cells)
p.SectionAssignment(region=region, sectionName='UHDC', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',
thicknessAssignment=FROM_SECTION)

# step
mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial', maxNumInc=10000, stabilizationMagnitude=0.0002, 
stabilizationMethod=DISSIPATED_ENERGY_FRACTION, continueDampingFactors=False, adaptiveDampingRatio=0.05, initialInc=0.01, maxInc=0.1, nlgeom=ON)
# mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'PE', 'PEEQ', 'PEMAG', 'LE', 'U',
# 'RF', 'CF', 'CSTRESS', 'CDISP', 'DAMAGEC', 'DAMAGET'))
mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'U', 'PE','RF','DAMAGEC', 'DAMAGET'))

# boundary conditions
myAssembly.ReferencePoint(point=(50.0, 50.0, 100.0))
r1 = myAssembly.referencePoints
refPoints1=(r1[2 * count + 3], )
region1=regionToolset.Region(referencePoints=refPoints1)
s1 = myAssembly.instances['Part-Base'].faces
side1Faces1 = s1.getSequenceFromMask(mask=('[#10 ]', ), )
region2=regionToolset.Region(side1Faces=side1Faces1)
mdb.models['Model-1'].Coupling(name='Constraint-2', controlPoint=region1, 
    surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, 
    localCsys=None, u1=ON, u2=ON, u3=ON, ur1=OFF, ur2=OFF, ur3=OFF)
r1 = myAssembly.referencePoints
refPoints1=(r1[2 * count + 3], )
region = regionToolset.Region(referencePoints=refPoints1)
mdb.models['Model-1'].EncastreBC(name='BC-1', createStepName='Initial', region=region, localCsys=None)

# load
mdb.models['Model-1'].TabularAmplitude(name='Amp-1', timeSpan=STEP, smooth=SOLVER_DEFAULT, data=((0.0, 0.0), (0.1, 0.1),
(0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)))
f1 = myAssembly.instances['Part-Base'].faces
faces1 = f1.getSequenceFromMask(mask=('[#20 ]', ), )
region = regionToolset.Region(faces=faces1)
mdb.models['Model-1'].DisplacementBC(name='load', createStepName='Step-1', 
    region=region, u1=0.0, u2=0.0, u3=10.0, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
    amplitude='Amp-1', fixed=OFF, distributionType=UNIFORM, fieldName='', 
    localCsys=None)

# mesh
## base
p = mdb.models['Model-1'].parts['Part-Base']
c = p.cells
pickedRegions = c.getSequenceFromMask(mask=('[#1 ]', ), )
p.setMeshControls(regions=pickedRegions, elemShape=TET, technique=FREE)
elemType1 = mesh.ElemType(elemCode=C3D20R)
elemType2 = mesh.ElemType(elemCode=C3D15)
elemType3 = mesh.ElemType(elemCode=C3D10)
cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
pickedRegions =(cells, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, 
    elemType3))
p.seedPart(size=10.0, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()

# job
mdb.Job(name='Job-1', model='Model-1', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=6, 
    numDomains=6, numGPUs=0)
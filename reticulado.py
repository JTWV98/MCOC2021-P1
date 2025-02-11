import numpy as np
from scipy.linalg import solve
import scipy.linalg as lin
import numpy as np
from scipy.linalg import solve
import h5py  
from barra import Barra
from secciones import SeccionICHA
from numpy import double

class Reticulado(object):
    """Define un reticulado"""
    __NNodosInit__ = 1

    #constructor
    def __init__(self):
        super(Reticulado, self).__init__()
        
        print("Constructor de Reticulado")
        self.Ndimensiones = 3
        self.xyz = np.zeros((Reticulado.__NNodosInit__,3), dtype=np.double)
        self.Nnodos = 0
        self.barras = []
        self.cargas = {}
        self.restricciones = {}
        
        """Implementar"""	
        


    def agregar_nodo(self, x, y, z=0):
        
        """Implementar"""	

        print(f"Quiero agregar un nodo en ({x} {y} {z})")
        numero_de_nodo_actual = self.Nnodos
        self.xyz.resize((numero_de_nodo_actual + 1,3))
        self.xyz[numero_de_nodo_actual,:] = [x, y, z]

        self.Nnodos += 1
        
        return 0

    def agregar_barra(self, barra):
        
        self.barras.append(barra)        
        
        return 0

    def obtener_coordenada_nodal(self, n):
        
        """Implementar"""	
     
        coordenada_nodal = self.xyz[n]
        print(f"{n}: {coordenada_nodal}")
        return (coordenada_nodal)
        
        
        
        
    def calcular_peso_total(self):
        
        """Implementar"""	
        
        peso_total = 0
        for i in self.barras:
            peso_total += i.calcular_peso(self)
        return peso_total
        
        
        
        
        
        return 0

    def obtener_nodos(self):
        
        return self.xyz

    def obtener_barras(self):
        
        return self.barras

  ##################################################  ENTREGA 3  
    
    
    def agregar_restriccion(self, nodo, gdl, valor=0.0):

        if nodo not in self.restricciones:
           
            self.restricciones[nodo] = [[gdl, valor]]
        else:
            self.restricciones[nodo].append([gdl, valor])
        
        
        return 0
     
        

    def agregar_fuerza(self, nodo, gdl, valor):
        
               
        if nodo in self.cargas:
            self.cargas[nodo].append = ([gdl, valor])
        
        else:
            self.cargas[nodo] = [[gdl, valor]]
     
        return 0

        # if no_existe_fuerza_pal_nodo:
        #     self.cargas[nodo] = []
            
        # self.cargas[nodo].append(gdl, valor)
        
        # return 0


    def ensamblar_sistema(self, factor_peso_propio=0.):
        #Ensamblar rigides y vector de cargas
       
        Ngdl = self.Nnodos * self.Ndimensiones

        self.K = np.zeros((Ngdl,Ngdl), dtype=np.double)
        self.f = np.zeros((Ngdl), dtype=np.double)
        self.u = np.zeros((Ngdl), dtype=np.double)
        
  

    
        for e in self.barras:   #recorrer barras
            ni = e.ni
            nj = e.nj
            
            k_e = e.obtener_rigidez(self)
            f_e = e.obtener_vector_de_cargas(self)
            
            
            d = [3*ni, 3*ni+1, 3*ni+2, 3*nj, 3*nj+1, 3*nj+2]
            
            
            #Aplicamos el metodo rigidez directa visto en los videos
            
            for i in range(6):
                p = d[i]
                for j in range(6):
                    q = d[j]
                    self.K[p,q] += k_e[i,j]
                self.f[p] += f_e[i]        
   

        
        return 0

        

    def resolver_sistema(self):
        
        numero_grado_libertad = self.Nnodos * self.Ndimensiones
        gdl_libres = np.arange(numero_grado_libertad)
        gdl_fijos = []
        
        for i in self.restricciones:
             for restriccion in self.restricciones[i]:
                  grado, valor = restriccion[0], restriccion[1]
                  gdl_general = grado + self.Ndimensiones*i
                  self.u[gdl_general] = valor
                  gdl_fijos.append(gdl_general)
        
        gdl_fijos = np.array(gdl_fijos)
        gdl_libres = np.setdiff1d(gdl_libres, gdl_fijos)
        
        for k in self.cargas:
            for z in self.cargas[k]:
                grado, valor = z[0], z[1]
                gdl_general = grado + self.Ndimensiones*k
                self.f[gdl_general] = valor
      
        Kff = self.K[np.ix_(gdl_libres, gdl_libres)]
        Kcc = self.K[np.ix_(gdl_fijos,gdl_fijos)]
        Kfc = self.K[np.ix_(gdl_libres,gdl_fijos)]
        Kcf = self.K[np.ix_(gdl_fijos,gdl_libres)]
        uf, uc = self.u[gdl_libres], self.u[gdl_fijos]
        ff, fc = self.f[gdl_libres], self.f[gdl_fijos]
        uf = solve(Kff, ff - Kfc @ uc)
        R = Kcf@uf+Kcc@uc-fc
        
        ### FINALMENTE ###
        self.u[gdl_libres] = uf
        self.R = R
        self.Kff = Kff
        self.Kcc = Kcc
        self.Kfc = Kfc
        self.Kcf = Kcf
       

        return 0

    

 
    def obtener_desplazamiento_nodal(self, n):
        
        if self.Ndimensiones == 2:
            dofs = [2*n, 2*n+1]
        elif self.Ndimensiones == 3:
            dofs = [3*n, 3*n+1, 3*n+2]
        
        return self.u[dofs]
        


    def obtener_fuerzas(self):
        
        fuerzas = np.zeros((len(self.barras)), dtype=np.double)
        for i,b in enumerate(self.barras):
            fuerzas[i] = b.obtener_fuerza(self)



        return fuerzas              






    def obtener_factores_de_utilizacion(self, f, ϕ=0.9):
        
        FU = np.zeros((len(self.barras)), dtype=np.double)
        for i,b in enumerate(self.barras):
            FU[i] = b.obtener_factor_utilizacion(f[i], ϕ)

        return FU



    



    def rediseñar(self, Fu, ϕ=0.9):
        
        """Implementar"""	
        
        return 0

    def chequear_diseño(self, Fu, ϕ=0.9):
        cumple = True
        for i,b in enumerate(self.barras):
            if not b.chequear_diseño(Fu[i], self, ϕ):
                print(f"----> Barra {i} no cumple algun criterio. ")
                cumple = False
        return cumple


    def guardar(self, nombre):

 	    dataset = h5py.File(nombre, "w")   
 	    dataset["xyz"] = self.xyz
         
 
 	    restricciones = np.zeros((10,2), dtype= np.int32)
 	    contador = 0
 	    # restricciones= np.array(restricciones,dtype=h5.string_dtype())        
 	    for restriccion in (self.restricciones):

              for valor_restriccion in (self.restricciones[restriccion]):
                
                restricciones[contador,0] = restriccion
                restricciones[contador,1] = valor_restriccion[0]
  
                contador += 1
                     
 	    dataset["restricciones"] = restricciones
   
 	    secciones = np.zeros((len(self.barras),), dtype= h5py.string_dtype())
 	    barras = np.zeros((len(self.barras),2), dtype= np.int32)        
 	    for numero_barra,barra in enumerate(self.barras):
              barras[numero_barra,0] = barra.ni
              barras[numero_barra,1] = barra.nj
              secciones[numero_barra] = barra.seccion.nombre()
 	    dataset["barras"] = barras
 	    dataset["secciones"] = secciones
         
         
         
 	    cargas = []
 	    for n in self.cargas:
               for cargas_ in self.cargas[n]:
                 cargas.append([n,cargas_[0]])
 	    dataset["cargas"]=cargas
 	     
        
        
 	    cargas_val = []
 	    for nodo in self.cargas:
               for cargval in self.cargas[nodo]:
                 cargas_val.append(cargval[1])
 	    dataset["cargas_val"]=cargas_val
 	    
 	    restricciones_val = []
 	    for n in self.restricciones:
               for restricciones_ in self.restricciones[n]:
                 restricciones_val.append(restricciones_[1])       
 	    dataset["restricciones_val"] = restricciones_val
        

 	
 	    return 0

    def abrir(self, nombre):

       
 	     dataset = h5py.File(nombre, "r")   
 	     dataset["xyz"] = self.xyz

 	     secciones_p6 = dataset["secciones"]
 	     restricciones_p6 = dataset["restricciones"]
 	     restricciones_val = dataset["restricciones_val"]
 	     cargas_p6 = dataset["cargas"]
 	     cargas_val = dataset["cargas_val"]
 	     barras_p6 = dataset["barras"]
 	     xyz_p6 = dataset["xyz"]

         #Cargas puntuales
 	     m = 0 
 	     for i in cargas_p6:
               valor_iterado = cargas_val[m][0]
               self.agregar_fuerza(i[0],i[1], valor_iterado)
               m += 1

        
        #Restricciones
 	     l=0
 	     for i in restricciones_p6:           
               valor_iterado=restricciones_val[l]
               self.agregar_restriccion(i[0],i[1], valor_iterado)
               l+=1
 
         #Barras
 	     o = 0
 	     for i in barras_p6:
               valor_iterado = dataset["secciones"][o]
               self.agregar_barra(i[0],i[1], SeccionICHA(str(valor_iterado)))
               o += 1

         #Nodos 
 	     for i in xyz_p6:
               self.agregar_nodo(i[0], i[1], i[2])


 	     return 0       


    def __str__(self):
        
        s="nodos: \n"
        for i in range(self.Nnodos):
            s+=f"\t {i}: ({self.xyz[i][0]} {self.xyz[i][1]} {self.xyz[i][2]}) \n"
        s+="\n"
        
        s+="barras: \n"
        for i,j in enumerate(self.barras,start=0):
            s+=f"\t {i}: [{j.ni} {j.nj}] \n"
        s+="\n"
        
        s+="restricciones: \n"
        for i in self.restricciones:
            s+=f"\t {i}: {self.restricciones[i]} \n"
        s+="\n"
        
        s+="cargas: \n"
        for i in self.cargas:
            s+=f"\t {i}: {self.cargas[i]} \n"
        s+="\n"
        
        s+="desplazamientos: \n"
        i=0
        j=0
        while i < (len(self.u)):
            s+=f"\t {j}: ({(self.u[i])}, {(self.u[i+1])}, {(self.u[i+2])}) \n"
            i+=3
            j+=1
        s+="\n"
        
        s+="fuerzas: \n" 
        for i,j in enumerate(self.barras,start=0):
            s+=f"\t {i}: {j.obtener_fuerza(self)} \n"
        s+="\n"
        
        
        return s
//Multilateration zur Berechung von Positionen

#include <stdio.h>
#include <math.h>

#define BASES 10	//Max Anz an Basen


struct vector3d{
    double x;
    double y;
    double z;
};


//Anz der Basen
int n = 0;
//Koord der Basen
double base_x[BASES];
double base_y[BASES];
double base_z[BASES];
//Abstaende zu den Basen
double r[BASES];

double start_x = 10000;
double start_y = 10000;
double start_z = 10000;

double posx = 0;
double posy = 0;
double posz = 0;

//muss so sein
double erg[3];


double *grad_f(double x, double y, double z, int n);
double f(double x, double y, double z, int n);
double armijo(double x, double y, double z, int n);
//struct vector3d rechne(void);
int rechne(void);




struct vector3d wrapper (double station[][3], double start[3], double radius[], int nn) {
//int wrapper (double station[][3], double start[3], double radius[], int nn) {
  printf("start\n");
  int i=0;
  printf("start\n");

  for (i = 0; i< nn; i++) {
	printf("n=%d -> %lf %lf %lf\n", i, station[i][0],station[i][1],station[i][2]);
  }
  for (i=0;i<nn;i++) {
    base_x[i] = station[i][0];
    base_y[i] = station[i][1];
    base_z[i] = station[i][2];
    r[i] = radius[i];
  }
  n = nn;
  start_x = start[0];
  start_y = start[1];
  start_z = start[2];
  
  printf("berechne\n");
  
  rechne();
  struct vector3d t;
  //vector3d t;
  t.x = 5.3;
  t.y = 0.9;
  t.z = 3.0;
  return t;
}

double wrapperx (double station[][3], double start[3], double radius[], int nn) {
//int wrapper (double station[][3], double start[3], double radius[], int nn) {
  int i=0;
  for (i=0;i<nn;i++) {
    base_x[i] = station[i][0];
    base_y[i] = station[i][1];
    base_z[i] = station[i][2];
    r[i] = radius[i];
  }
  n = nn;
  start_x = start[0];
  start_y = start[1];
  start_z = start[2];
  
  printf("berechne x\n");
  
  rechne();
  return posx;
}

double wrappery (double station[][3], double start[3], double radius[], int nn) {
//int wrapper (double station[][3], double start[3], double radius[], int nn) {
  int i=0;
  for (i=0;i<nn;i++) {
    base_x[i] = station[i][0];
    base_y[i] = station[i][1];
    base_z[i] = station[i][2];
    r[i] = radius[i];
  }
  n = nn;
  start_x = start[0];
  start_y = start[1];
  start_z = start[2];
  
  printf("berechne y\n");
  
  rechne();
  return posy;
}

double wrapperz (double station[][3], double start[3], double radius[], int nn) {
//int wrapper (double station[][3], double start[3], double radius[], int nn) {
  int i=0;
  for (i=0;i<nn;i++) {
    base_x[i] = station[i][0];
    base_y[i] = station[i][1];
    base_z[i] = station[i][2];
    r[i] = radius[i];
  }
  n = nn;
  start_x = start[0];
  start_y = start[1];
  start_z = start[2];
  
  printf("berechne z\n");
  
  rechne();
  return posz;
}



int rechne() {
	//double temp = 0.0;

	double *richtung;
	double schritt = 0.0;
	double x = start_x;
	double y = start_y;
	double z = start_z;
	double x_neu = 0.0;
	double y_neu = 0.0;
	double z_neu = 0.0;
	int i = 0;
	//test();	//test-Daten	

	//double funkt = 0.0;
	//funkt = f(x,y,z,n);
	//printf("funktion: %lf\n",funkt);	

	

	while(i<2000)
	{
	  //printf("iter:%d\n",i);
		richtung = grad_f(x,y,z,n);
		//printf("richtung: %lf  ", richtung[0]);
		//richtung[0] = -richtung[0];
		//printf("richtung-neg: %lf  ", richtung[0]);
		//richtung[1] = -richtung[1];
		//richtung[2] = -richtung[2];
		schritt = armijo(x,y,z,n);

		x_neu = x - schritt*richtung[0];
		y_neu = y - schritt*richtung[1];
		z_neu = z - schritt*richtung[2];
		i++;
		//auf Staionaritaet pruefen
		if (((x-x_neu)*(x-x_neu)+(y-y_neu)*(y-y_neu)+(z-z_neu)*(z-z_neu))<0.0001)
			break;
		x = x_neu;
		y = y_neu;
		z = z_neu;
		//funkt = f(x,y,z,n);
		//printf("schritt: %lf  ",schritt);
		//temp = schritt*richtung[0];
		//printf("multi: %lf\n", temp);

	}

	x = x_neu;
	y = y_neu;
	z = z_neu;
    
    posx = x;
    posy = y;
    posz = z;

	printf("Iterationen: %i  Position: x = %lf, y = %lf, z = %lf\n",i,x,y,z);
int ret =0;
	return ret;
}

//zu minimierende Funktion f
double f(double x, double y, double z, int n) {

	int i = 0;
	double erg3 = 0.0;
	double zwi = 0.0;

	for(i = 0; i < n; i++)
	{
		zwi = (x-base_x[i])*(x-base_x[i])+(y-base_y[i])*(y-base_y[i])+(z-base_z[i])*(z-base_z[i])-r[i]*r[i];
		//printf("zwi: %d, %lf\n", i, zwi);
		erg3 += zwi*zwi;
	}
	return erg3;

}

// grad(f)
double *grad_f(double x, double y, double z, int n) {

	
	erg[0] = 0.0; erg[1] = 0.0; erg[2] = 0.0;
	int i = 0;
	double zwi = 0.0;
	//x-Komp
	for (i = 0; i < n; i++)
	{
		zwi = (x-base_x[i])*(x-base_x[i])+(y-base_y[i])*(y-base_y[i])+(z-base_z[i])*(z-base_z[i])-r[i]*r[i];
		erg[0] += zwi * (x-base_x[i]);
		

	}
	erg[0] = erg[0] *4;
	//y-Komp
	for (i = 0; i < n; i++)
	{
		zwi = (x-base_x[i])*(x-base_x[i])+(y-base_y[i])*(y-base_y[i])+(z-base_z[i])*(z-base_z[i])-r[i]*r[i];
		erg[1] += zwi * (y-base_y[i]); 
		
	}
	erg[1] = erg[1] *4;
	//z-Komp
	for (i = 0; i < n; i++)
	{
		zwi = (x-base_x[i])*(x-base_x[i])+(y-base_y[i])*(y-base_y[i])+(z-base_z[i])*(z-base_z[i])-r[i]*r[i];
		erg[2] += zwi * (z-base_z[i]);
		
	}
	erg[2] = erg[2] *4;


	return erg;

}

//armijo-Schrittweite bestimmen
double armijo(double x, double y, double z, int n) {

	double schritt = 1;
	int i = 0;
	double ls = 0.0;
	double rs = 0.0;
	double *gradient;
	gradient = grad_f(x,y,z,n);

	while (i < 5000)
	{
		ls = f(x+schritt*(-gradient[0]),y+schritt*(-gradient[1]),z+schritt*(-gradient[2]),n);
		rs = f(x,y,z,n) + 0.5*schritt*(-gradient[0]*gradient[0]-gradient[1]*gradient[1]-gradient[2]*gradient[2]);
		if (ls <= rs)
			break;
		schritt = schritt / 2;
		i++;
	}

	return schritt;

}

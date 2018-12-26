#include <stdio.h>
#include <math.h>

#define maxSize 100
#define Length 78
#define Threshold -50 
#define TRUE 1
#define FALSE 0
#define EPS (1e-06)
#define ABS(x) (fabs(x))
#define MIN(a,b) (a<b ? a:b)
#define MAX(a,b) (a>b ? a:b)

typedef struct WAP{
	float x,y;
	float power;	//in dBm
	float freq;    //in GHz
}WAP;

typedef struct Point{
	float x, y;
}Point;

typedef struct line_t{
	Point p1, p2;
}line_t;

int line_intersect(line_t, line_t);

float Distance(float x1, float y1, float x2, float y2){
	return sqrt(pow((x1 - x2), 2) + pow((y1 - y2), 2));
}

float FSPL(float d, float f){
	return 20 * log10(d) + 20 * log10(f) + 32.45;
}

float Strength(WAP wap, float x, float y){
	float d, loss;
	d = Distance(x, y, wap.x, wap.y);
	loss = FSPL(d, wap.freq);
	return wap.power - loss;
}



float MaxInPoint(WAP wapList[], int n, float x, float y){
	float maxStren, curStren;
	int i = 0;
	maxStren = Strength(wapList[0], x, y);
	for (i = 1; i < n; i++){
		curStren = Strength(wapList[i], x, y);
		if(curStren > maxStren)
			maxStren = curStren;
	}
	return maxStren;
}

void DrawMap(WAP wapList[], int n){
	float i, j;
	float cur;
	for(j = 77.0; j > 0; j = j - 2){
		for(i = 0.5; i < 78; i = i + 1){
			cur = MaxInPoint(wapList, n, i, j);
			if (cur > 0)
				printf("+");
			else if (cur > -10)
				printf(" ");
			else if (cur > -20)
				printf("2");
			else if (cur > -30)
				printf(" ");
			else if (cur > -40)
				printf("4");
			else if (cur > -50)
				printf(" ");
			else
				printf("-");
		}
		printf("\n");
	}
		
}

int InBound(line_t l[], int m, Point cent, Point p){
	line_t curline;
	curline.p1 = cent;
	curline.p2 = p;
	int i;
	for (i = 0; i <= m; i++){
		if (line_intersect(curline, l[i]))
			return 0;
	}
	return 1;
}

void DrawMap2(WAP wapList[], int n, line_t l[], int m, Point cent){
	float i, j;
	float cur;
	Point p;
	for(j = 77.0; j > 0; j = j - 2){
		for(i = 0.5; i < 78; i = i + 1){
			p.x = i;
			p.y = j;
			if (!InBound(l, m, cent, p)){
				printf("#");
				continue;
			}
			cur = MaxInPoint(wapList, n, i, j);
			if (cur > 0)
				printf("+");
			else if (cur > -10)
				printf(" ");
			else if (cur > -20)
				printf("2");
			else if (cur > -30)
				printf(" ");
			else if (cur > -40)
				printf("4");
			else if (cur > -50)
				printf(" ");
			else
				printf("-");
		}
		printf("\n");
	}
		
}

int line_intersect(line_t l1, line_t l2) {
   float x1=l1.p1.x, y1=l1.p1.y,
   	  x2=l1.p2.x, y2=l1.p2.y,
   	  x3=l2.p1.x, y3=l2.p1.y,
   	  x4=l2.p2.x, y4=l2.p2.y;
   float mua,mub;
   float denom,numera,numerb;

   /* Take the projections of the two line segments */
   float xMin1, xMax1, xMin2, xMax2, yMin1, yMax1, yMin2, yMax2;
   xMin1 = MIN(x1, x2);
   xMax1 = MAX(x1, x2);
   xMin2 = MIN(x3, x4);
   xMax2 = MAX(x3, x4);

   yMin1 = MIN(y1, y2);
   yMax1 = MAX(y1, y2);
   yMin2 = MIN(y3, y4);
   yMax2 = MAX(y3, y4);
   
   /* Do the projects intersect? */
   if((xMin2-xMax1) >= EPS || (xMin1-xMax2) >= EPS || 
   	   (yMin2-yMax1) >= EPS || (yMin1-yMax2) >= EPS) {
   	   return FALSE;
   }

   denom  = (y4-y3) * (x2-x1) - (x4-x3) * (y2-y1);
   numera = (x4-x3) * (y1-y3) - (y4-y3) * (x1-x3);
   numerb = (x2-x1) * (y1-y3) - (y2-y1) * (x1-x3);

   /* Are the line coincident? */
   if (ABS(numera) < EPS && ABS(numerb) < EPS && ABS(denom) < EPS) {
      return(TRUE);
   }

   /* Are the line parallel */
   if (ABS(denom) < EPS) {
      return(FALSE);
   }

   /* Is the intersection along the the segments */
   mua = numera / denom;
   mub = numerb / denom;
   /* AM - use equality here so that "on the end" is not an
    * intersection; use strict inequality if "touching at end" is an
    * intersection */
   if (mua < 0 || mua > 1 || mub < 0 || mub > 1) {
      return(FALSE);
   }
   return(TRUE);
}

void main(){
	WAP wapList[maxSize];
	int i, j, n;
	float max = 0.0;
	char type;
	// stage 1 input
	i = 0;
	while(scanf("%c", &type) == 1 && type == 'W'){
		scanf("%f %f %f %f\n",&(wapList[i].x), &(wapList[i].y), &(wapList[i].power), &(wapList[i].freq));
		i++;
	}
	n = i;
	// stage 1 output
	printf("Stage 1\n");
	printf("==========\n");
	printf("Number of WAPs: %02d\n", n);
	printf("Maximum signal strength at (00.0, 00.0): %5.2f dBm\n", MaxInPoint(wapList, n, 0, 0));
	// stage 2 input
	Point point[maxSize];
	i = 0;
	while(type == 'P'){
		scanf("%f %f\n", &point[i].x, &point[i].y);
		i++;
		scanf("%c", &type);
	}
	// stage 2 output
	printf("\nStage 2\n");
	printf("==========\n");
	for(j = 0; j < i; j++){
		printf("Maximum signal strength at (%04.1f, %04.1f): %5.2f dBm\n", point[j].x, point[j].y, MaxInPoint(wapList, n, point[j].x, point[j].y));
	}
	
	// stage 3 input
	int count = 0, low = 0;
	for (i = 1; i < Length; i++)
		for (j = 1; j < Length; j++){
			if (MaxInPoint(wapList, n, i, j) <= Threshold)
				low++;
			count++;
		}
	// stage 3 output
	printf("\nStage 3\n");
	printf("==========\n");
	printf("%04d points sampled\n", count);
	printf("%04d points (%05.2f%%) with maximum signal strength <= -50 dBm\n", low, ((float)low / count * 100));
	
	// stage 4
	printf("\nStage 4\n");
	printf("==========\n");
	DrawMap(wapList, n);
	// stage 5 input
	line_t l[maxSize];
	int line_num = 0;
	Point centroid, p[maxSize];
	i = 0;
	float x_sum = 0, y_sum = 0;
	while(type == 'V'){
		scanf("%f %f\n", &p[i].x, &p[i].y);
		x_sum += p[i].x;
		y_sum += p[i].y;
		if (i){
			l[line_num].p1 = p[i-1];
			l[line_num].p2 = p[i];
			line_num++;
		}
		i++;
		if (scanf("%c", &type) != 1)
			break;
	}
	l[line_num].p1 = p[i-1];
	l[line_num].p2 = p[0];
	centroid.x = x_sum / (i-1);
	centroid.y = y_sum / (i-1);
	
	printf("\nStage 5\n");
	printf("==========\n");
	
	DrawMap2(wapList, n, l, line_num, centroid);
	
}
 

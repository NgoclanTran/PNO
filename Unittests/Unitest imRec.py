import unittest
from ImRec import *

# Here's our "unit".

# Here's our "unit tests".
class ImRecTests(unittest.TestCase):

    def setUp(self):
        self.Im = ImRec()
        self.Img = ['red_star.jpeg','yellow_square.jpeg','yellow_circle.jpeg','purple_square.jpeg','green_triangle.jpeg','yellow_square.jpeg','yellow_square.jpeg','yellow_square.jpeg','red_star.jpeg','red_star.jpeg','yellow_circle.jpeg','yellow_circle.jpeg','purple_star.jpeg','blue_circle.jpeg','purple_square.jpeg','purple_square.jpeg','green_triangle.jpeg','red_star.jpeg','purple_square.jpeg','green_circle.jpeg','blue_circle.jpeg','blue_circle.jpeg','green_triangle.jpeg','green_circle.jpeg','blue_circle.jpeg','yellow_star.jpeg','green_circle.jpeg','purple_circle.jpeg','purple_circle.jpeg','blue_square.jpeg','blue_square.jpeg','green_triangle.jpeg','yellow_circle.jpeg']

    def testOne(self):
        
        for i in range(1,34):

            result = self.Im.detectImage('IMG'+str(i)+'.jpg')
            self.assertEqual(result, self.Img[i-1])

def main():
    unittest.main()

if __name__ == '__main__':
    main()

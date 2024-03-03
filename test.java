class test{
    public static void main(String[] args){
        System.out.println("Hello World");
        System.out.println(gcd1(24,12));
    }

    public static int gcd(int m, int n){
        if(n==0){
            return m;
        }
        return gcd(n,m%n);
    }
    public static int gcd1(int m,int n){
        int t = Math.min(m, n);
        while(m%t!=0 || n%t!=0){
            t--;
        }
        System.out.println("Your answer is: " + t);
        return t;
    }

    
}